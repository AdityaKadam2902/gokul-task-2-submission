"""Patient management CRUD API endpoints.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db
from app.models.patient import Patient
from app.schemas.analysis import AnalysisDetailResponse, AnalysisSummary
from app.schemas.common import ErrorEnvelope
from app.schemas.patient import (
    PatientCreate,
    PatientListItem,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)
from app.services.analysis_service import AnalysisService
from app.services.patient_service import PatientService, get_latest_analysis

router = APIRouter(prefix="/patients", tags=["patients"])


def map_patient_to_response(patient: Patient) -> PatientResponse:
    """Map SQLAlchemy Patient model and latest analysis to PatientResponse schema."""
    latest_run = get_latest_analysis(patient)
    latest_summary = None
    if latest_run is not None:
        latest_summary = AnalysisSummary(
            id=latest_run.id,
            patient_id=latest_run.patient_id,
            run_number=latest_run.run_number,
            overall_status=latest_run.overall_status,
            external_status=latest_run.external_status,
            ai_status=latest_run.ai_status,
            external_provider=latest_run.external_provider,
            ai_model=latest_run.ai_model,
            remarks_text=latest_run.remarks_text,
            error_code=latest_run.error_code,
            created_at=latest_run.created_at,
            completed_at=latest_run.completed_at,
        )

    return PatientResponse(
        id=patient.id,
        full_name=patient.full_name,
        date_of_birth=patient.date_of_birth,
        email=patient.email,
        glucose_value=patient.glucose_value,
        haemoglobin_value=patient.haemoglobin_value,
        cholesterol_value=patient.cholesterol_value,
        unit_profile_code=patient.unit_profile_code,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
        latest_analysis=latest_summary,
    )


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Patient record created successfully."},
        409: {
            "model": ErrorEnvelope,
            "description": "Exact duplicate record detected. Requires allow_duplicate=true confirmation.",
        },
        422: {"model": ErrorEnvelope, "description": "Validation failure."},
    },
    summary="Create patient record",
    description=(
        "Validates input, checks for duplicate entries, persists patient to SQLite, "
        "and creates an initial PENDING analysis run."
    ),
)
def create_patient(
    data: PatientCreate,
    allow_duplicate: bool = Query(
        default=False,
        description="Explicitly permit inserting an exact duplicate record.",
    ),
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Create a new patient record."""
    if allow_duplicate:
        data.allow_duplicate = True
    patient, _ = PatientService.create_patient(db=db, data=data)
    return map_patient_to_response(patient)


@router.get(
    "",
    response_model=PatientListResponse,
    status_code=status.HTTP_200_OK,
    summary="List patient records",
    description="Retrieve paginated patient records ordered by created_at DESC with optional search.",
)
def list_patients(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(default=None, description="Optional search by full name or email"),
    db: Session = Depends(get_db),
) -> PatientListResponse:
    """Retrieve paginated patient records."""
    patients, total, total_pages = PatientService.list_patients(
        db=db, page=page, page_size=page_size, search=search
    )

    items: list[PatientListItem] = []
    for p in patients:
        latest = get_latest_analysis(p)
        items.append(
            PatientListItem(
                id=p.id,
                full_name=p.full_name,
                date_of_birth=p.date_of_birth,
                email=p.email,
                glucose_value=p.glucose_value,
                haemoglobin_value=p.haemoglobin_value,
                cholesterol_value=p.cholesterol_value,
                unit_profile_code=p.unit_profile_code,
                created_at=p.created_at,
                updated_at=p.updated_at,
                latest_analysis_status=latest.overall_status if latest else None,
                latest_remarks=latest.remarks_text if latest else None,
            )
        )

    return PatientListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Patient record retrieved successfully."},
        404: {"model": ErrorEnvelope, "description": "Patient not found."},
    },
    summary="Get patient by ID",
    description="Retrieve a single patient record by internal ID along with latest analysis summary.",
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Retrieve individual patient details."""
    patient = PatientService.get_patient_by_id(db, patient_id)
    return map_patient_to_response(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Patient updated successfully."},
        404: {"model": ErrorEnvelope, "description": "Patient not found."},
        409: {
            "model": ErrorEnvelope,
            "description": "Duplicate record conflict with another patient.",
        },
        422: {"model": ErrorEnvelope, "description": "Validation failure."},
    },
    summary="Update patient record",
    description=(
        "Partially updates patient fields. Name/email-only updates do not invalidate analysis. "
        "Clinical measurement or DOB updates generate a new analysis run."
    ),
)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    allow_duplicate: bool = Query(
        default=False,
        description="Explicitly permit updating to match an exact duplicate record.",
    ),
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Update patient fields."""
    if allow_duplicate:
        data.allow_duplicate = True
    patient, _ = PatientService.update_patient(db=db, patient_id=patient_id, data=data)
    return map_patient_to_response(patient)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Patient record deleted successfully."},
        404: {"model": ErrorEnvelope, "description": "Patient not found."},
    },
    summary="Delete patient record",
    description="Deletes a patient record and permanently cascades to its entire analysis history.",
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a patient record."""
    PatientService.delete_patient(db=db, patient_id=patient_id)


@router.get(
    "/{patient_id}/analyses",
    response_model=list[AnalysisDetailResponse],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Analysis history retrieved successfully."},
        404: {"model": ErrorEnvelope, "description": "Patient not found."},
    },
    summary="List patient analysis history",
    description="Retrieve full audit history of analysis runs for a patient ordered newest-first.",
)
def list_patient_analyses(
    patient_id: int,
    db: Session = Depends(get_db),
) -> list[AnalysisDetailResponse]:
    """List analysis runs for a patient."""
    runs = PatientService.list_analyses_for_patient(db=db, patient_id=patient_id)
    return [
        AnalysisDetailResponse(
            id=r.id,
            patient_id=r.patient_id,
            run_number=r.run_number,
            overall_status=r.overall_status,
            external_status=r.external_status,
            ai_status=r.ai_status,
            external_provider=r.external_provider,
            ai_model=r.ai_model,
            remarks_text=r.remarks_text,
            error_code=r.error_code,
            created_at=r.created_at,
            completed_at=r.completed_at,
            input_snapshot_json=r.input_snapshot_json,
            external_result_json=r.external_result_json,
            ai_result_json=r.ai_result_json,
            error_summary=r.error_summary,
            retry_of_id=r.retry_of_id,
        )
        for r in runs
    ]


@router.post(
    "/{patient_id}/analyses",
    response_model=AnalysisSummary,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Analysis scheduled."},
        404: {"model": ErrorEnvelope, "description": "Patient not found."},
        409: {"model": ErrorEnvelope, "description": "Analysis already in progress."},
    },
    summary="Trigger or retry patient analysis",
    description="Creates a new analysis run from current persisted values and schedules external interpretation asynchronously.",
)
async def trigger_patient_analysis(
    patient_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> AnalysisSummary:
    """Trigger or retry an analysis run."""
    analysis = AnalysisService.create_retry_analysis(db=db, patient_id=patient_id)
    bind = db.get_bind()
    factory = sessionmaker(bind=bind, autocommit=False, autoflush=False)
    background_tasks.add_task(
        AnalysisService.execute_analysis_run,
        analysis_id=analysis.id,
        session_factory=factory,
    )
    return AnalysisSummary(
        id=analysis.id,
        patient_id=analysis.patient_id,
        run_number=analysis.run_number,
        overall_status=analysis.overall_status,
        external_status=analysis.external_status,
        ai_status=analysis.ai_status,
        external_provider=analysis.external_provider,
        ai_model=analysis.ai_model,
        remarks_text=analysis.remarks_text,
        error_code=analysis.error_code,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
    )


@router.get(
    "/{patient_id}/analyses/{analysis_id}",
    response_model=AnalysisDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Analysis detail retrieved."},
        404: {"model": ErrorEnvelope, "description": "Patient or analysis not found."},
    },
    summary="Get analysis run detail",
    description="Retrieve specific analysis run detail for a patient.",
)
def get_patient_analysis(
    patient_id: int,
    analysis_id: str,
    db: Session = Depends(get_db),
) -> AnalysisDetailResponse:
    """Retrieve specific analysis run detail."""
    r = PatientService.get_analysis_by_id(db=db, patient_id=patient_id, analysis_id=analysis_id)
    return AnalysisDetailResponse(
        id=r.id,
        patient_id=r.patient_id,
        run_number=r.run_number,
        overall_status=r.overall_status,
        external_status=r.external_status,
        ai_status=r.ai_status,
        external_provider=r.external_provider,
        ai_model=r.ai_model,
        remarks_text=r.remarks_text,
        error_code=r.error_code,
        created_at=r.created_at,
        completed_at=r.completed_at,
        input_snapshot_json=r.input_snapshot_json,
        external_result_json=r.external_result_json,
        ai_result_json=r.ai_result_json,
        error_summary=r.error_summary,
        retry_of_id=r.retry_of_id,
    )
