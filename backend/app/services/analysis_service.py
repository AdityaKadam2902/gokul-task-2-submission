"""Analysis lifecycle, provider orchestration, and local AI remark generation service.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import AppException, ResourceNotFoundException
from app.db.session import SessionLocal
from app.integrations.ollama.generator import OllamaRemarksGenerator
from app.integrations.testwell.adapter import TestWellAdapter
from app.integrations.testwell.exceptions import TestWellError
from app.models.base import get_utc_now
from app.models.enums import AiStatus, ExternalStatus, OverallStatus
from app.models.patient import Patient
from app.models.patient_analysis import PatientAnalysis
from app.services.patient_service import build_anonymous_input_snapshot

logger = logging.getLogger(__name__)


class AnalysisService:
    """Orchestrates external health API analysis runs, local AI remarks, retries, and persistence."""

    @staticmethod
    async def execute_analysis_run(
        analysis_id: str,
        adapter: TestWellAdapter | None = None,
        generator: OllamaRemarksGenerator | None = None,
        session_factory: sessionmaker[Session] | None = None,
    ) -> PatientAnalysis:
        """Execute an analysis run through TestWell and local Ollama llama3.2:3b.

        CRITICAL ARCHITECTURAL RULES:
        1. Zero database locks or open transactions are held across external HTTP or local AI calls.
        2. TestWell result is validated and normalized first.
        3. Local Ollama remarks generator receives only normalized observations and caveats (NO PII).
        4. If Ollama fails or safety validation rejects output, deterministic fallback is safely applied.
        """
        adapter = adapter or TestWellAdapter()
        ollama_generator = generator or OllamaRemarksGenerator()
        factory = session_factory or SessionLocal

        # --- Phase 1: Retrieve input snapshot & mark run started (Short DB session) ---
        try:
            with factory() as db:
                analysis = db.scalar(
                    select(PatientAnalysis).where(PatientAnalysis.id == analysis_id)
                )
                if analysis is None:
                    raise ResourceNotFoundException("Analysis", analysis_id)

                patient = db.scalar(select(Patient).where(Patient.id == analysis.patient_id))
                if patient is None:
                    raise ResourceNotFoundException("Patient", analysis.patient_id)

                glucose_val = patient.glucose_value
                haemoglobin_val = patient.haemoglobin_value
                cholesterol_val = patient.cholesterol_value
                unit_profile = patient.unit_profile_code

                analysis.started_at = get_utc_now()
                analysis.external_status = ExternalStatus.PENDING
                analysis.overall_status = OverallStatus.PENDING
                db.commit()
        except Exception as phase1_err:
            logger.error("Failed to initialize analysis run %s: %s", analysis_id, phase1_err)
            raise

        # --- Phase 2: External HTTP Call to TestWell (Zero DB Transactions Open) ---
        normalized_result = None
        dispatch_error: Exception | None = None

        try:
            normalized_result = await adapter.interpret_biomarkers(
                glucose_value=glucose_val,
                haemoglobin_value=haemoglobin_val,
                cholesterol_value=cholesterol_val,
                unit_profile_code=unit_profile,
            )
        except TestWellError as err:
            logger.warning("TestWell provider returned error for analysis %s: %s", analysis_id, err)
            dispatch_error = err
        except Exception as unhandled:
            logger.error(
                "Unhandled error invoking TestWell for analysis %s: %s", analysis_id, unhandled
            )
            dispatch_error = unhandled

        # --- Phase 3: Local Ollama AI Remarks Generation (Zero DB Transactions Open) ---
        ai_remarks_text: str | None = None
        ai_result_json: dict[str, Any] | None = None
        is_ai_generated: bool = False

        if normalized_result is not None and normalized_result.summary.get("matched", 0) > 0:
            # Generate remarks from normalized TestWell observations
            (
                ai_remarks_text,
                ai_result_json,
                is_ai_generated,
                _ai_latency,
            ) = await ollama_generator.generate_remarks(normalized_result)

        # --- Phase 4: Persist Analysis Results & Final Statuses (Short DB session) ---
        with factory() as db:
            analysis = db.scalar(select(PatientAnalysis).where(PatientAnalysis.id == analysis_id))
            if analysis is None:
                raise ResourceNotFoundException("Analysis", analysis_id)

            completed_timestamp = get_utc_now()
            analysis.completed_at = completed_timestamp

            if normalized_result is not None:
                # Successful provider interpretation
                result_dict: dict[str, Any] = normalized_result.model_dump()
                analysis.external_result_json = result_dict
                analysis.external_api_version = normalized_result.api_version
                analysis.ruleset_version = "testwell-normalizer-v1"

                matched_count = normalized_result.summary.get("matched", 0)
                total_count = normalized_result.summary.get("total", 0)
                has_unit_mismatch = any(obs.unit_mismatch for obs in normalized_result.observations)

                if matched_count == 0:
                    # None of the markers could be recognized
                    analysis.external_status = ExternalStatus.NO_MATCH
                    analysis.overall_status = OverallStatus.FAILED
                    analysis.ai_status = AiStatus.NOT_RUN
                    analysis.error_code = "NO_MATCHING_BIOMARKERS"
                    analysis.error_summary = "None of the submitted laboratory markers were recognized in the provider reference catalog."
                else:
                    # At least one marker matched
                    analysis.external_status = ExternalStatus.SUCCEEDED
                    analysis.remarks_text = ai_remarks_text
                    analysis.ai_result_json = ai_result_json
                    analysis.ai_provider = "ollama"
                    analysis.ai_model = ollama_generator.client.model
                    analysis.prompt_version = "labinsight-v1"

                    is_provider_degraded = (matched_count < total_count) or has_unit_mismatch

                    if is_ai_generated:
                        # Full successful AI remarks generation
                        analysis.ai_status = AiStatus.SUCCEEDED
                        if is_provider_degraded:
                            analysis.overall_status = OverallStatus.DEGRADED
                            analysis.error_code = (
                                "PARTIAL_PROVIDER_MATCH"
                                if not has_unit_mismatch
                                else "UNIT_MISMATCH_DETECTED"
                            )
                            analysis.error_summary = "One or more biomarkers had unit mismatches or were not recognized in provider catalog."
                        else:
                            analysis.overall_status = OverallStatus.COMPLETED
                            analysis.error_code = None
                            analysis.error_summary = None
                    else:
                        # Deterministic fallback used
                        analysis.ai_status = AiStatus.FALLBACK
                        analysis.overall_status = OverallStatus.DEGRADED
                        analysis.error_code = "AI_FALLBACK_APPLIED"
                        analysis.error_summary = (
                            "AI remarks unavailable; deterministic provider information shown."
                        )

            else:
                # Provider failure: AI is NOT_RUN
                analysis.external_status = ExternalStatus.FAILED
                analysis.overall_status = OverallStatus.FAILED
                analysis.ai_status = AiStatus.NOT_RUN

                if isinstance(dispatch_error, TestWellError):
                    analysis.error_code = dispatch_error.error_code
                    analysis.error_summary = dispatch_error.error_summary
                else:
                    analysis.error_code = "TESTWELL_CALL_FAILED"
                    analysis.error_summary = (
                        "An unexpected error occurred while communicating with external health API."
                    )

            db.commit()
            db.refresh(analysis)
            return analysis

    @staticmethod
    def create_retry_analysis(db: Session, patient_id: int) -> PatientAnalysis:
        """Create or locate an eligible pending analysis run for a patient.

        Lifecycle Rules (Phase 4B Correction):
        1. Guard: Check if an analysis is actively running (PENDING with started_at is not None).
           If so, raise HTTP 409 conflict.
        2. First Trigger: If an existing unstarted initial pending analysis exists (started_at is None),
           reuse and return that record rather than creating an extra orphaned run.
        3. Retry Trigger: If all prior runs are in terminal state (COMPLETED, DEGRADED, FAILED),
           create a genuine retry row with run_number = highest + 1 and retry_of_id pointing to prior run.
        """
        patient = db.scalar(select(Patient).where(Patient.id == patient_id))
        if patient is None:
            raise ResourceNotFoundException("Patient", patient_id)

        # 1. Guard: Check if an analysis is currently running
        active_running = db.scalar(
            select(PatientAnalysis).where(
                PatientAnalysis.patient_id == patient_id,
                PatientAnalysis.overall_status == OverallStatus.PENDING,
                PatientAnalysis.started_at.is_not(None),
            )
        )
        if active_running is not None:
            raise AppException(
                message=f"An analysis run (ID: {active_running.id}) is already currently in progress for this patient.",
                code="ANALYSIS_IN_PROGRESS",
                status_code=409,
            )

        # 2. Check for an unstarted pending analysis run (e.g. initial run from patient creation)
        unstarted_pending = db.scalar(
            select(PatientAnalysis)
            .where(
                PatientAnalysis.patient_id == patient_id,
                PatientAnalysis.overall_status == OverallStatus.PENDING,
                PatientAnalysis.started_at.is_(None),
            )
            .order_by(PatientAnalysis.run_number.asc())
        )
        if unstarted_pending is not None:
            # Reuse the existing initial unstarted pending record!
            return unstarted_pending

        # 3. Genuine retry: determine highest run and link to previous run
        existing_runs = db.scalars(
            select(PatientAnalysis).where(PatientAnalysis.patient_id == patient_id)
        ).all()
        highest_run = max([r.run_number for r in existing_runs], default=0)
        latest_run = max(existing_runs, key=lambda r: r.run_number) if existing_runs else None

        snapshot = build_anonymous_input_snapshot(
            glucose_value=patient.glucose_value,
            haemoglobin_value=patient.haemoglobin_value,
            cholesterol_value=patient.cholesterol_value,
            unit_profile_code=patient.unit_profile_code,
        )

        new_analysis = PatientAnalysis(
            patient_id=patient.id,
            run_number=highest_run + 1,
            input_snapshot_json=snapshot,
            external_provider="testwell",
            external_status=ExternalStatus.PENDING,
            ai_provider="ollama",
            ai_model="llama3.2:3b",
            ai_status=AiStatus.NOT_RUN,
            overall_status=OverallStatus.PENDING,
            retry_of_id=latest_run.id if latest_run else None,
        )

        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        return new_analysis

    @staticmethod
    def get_analysis_detail(db: Session, patient_id: int, analysis_id: str) -> PatientAnalysis:
        """Retrieve detailed analysis run including provider observations and AI remarks."""
        analysis = db.scalar(
            select(PatientAnalysis).where(
                PatientAnalysis.id == analysis_id,
                PatientAnalysis.patient_id == patient_id,
            )
        )
        if analysis is None:
            raise ResourceNotFoundException("Analysis", analysis_id)
        return analysis
