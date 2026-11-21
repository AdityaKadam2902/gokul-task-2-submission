"""LabInsight Demonstration Data Seeder.

Seeds realistic patient records, TestWell observations, and Ollama AI remarks
for demonstrations, walkthrough videos, and technical reviews.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import argparse
import os
import sys
from datetime import UTC, date, datetime
from decimal import Decimal

# Ensure backend modules are discoverable
sys.path.insert(0, os.path.abspath("backend"))

from app.db.session import SessionLocal
from app.models.enums import AiStatus, ExternalStatus, OverallStatus
from app.models.patient import Patient
from app.models.patient_analysis import PatientAnalysis
from sqlalchemy import delete, func, select


def build_observations(glucose: float, hb: float, chol: float) -> list[dict]:
    """Generate realistic TestWell normalized observations for the 3 blood markers."""
    # Glucose interpretation
    if glucose < 70:
        g_flag = "low"
        g_guide = (
            "Value is below standard fasting range (70-99 mg/dL), consistent with hypoglycemia."
        )
    elif glucose <= 99:
        g_flag = "normal"
        g_guide = "Value aligns with normal adult fasting plasma glucose reference intervals."
    elif glucose <= 125:
        g_flag = "borderline_high"
        g_guide = "Value is in the impaired fasting glucose / pre-diabetes educational interval (100-125 mg/dL)."
    else:
        g_flag = "high"
        g_guide = "Value exceeds 126 mg/dL, in the elevated educational range consistent with hyperglycemia."

    # Haemoglobin interpretation
    if hb < 12.0:
        h_flag = "low"
        h_guide = "Value is below standard adult reference range (12.0-17.5 g/dL), indicating possible anemia."
    elif hb <= 17.5:
        h_flag = "normal"
        h_guide = (
            "Value falls comfortably within the normal reference range for adult blood specimens."
        )
    else:
        h_flag = "high"
        h_guide = "Value is elevated above normal adult reference range (17.5 g/dL)."

    # Cholesterol interpretation
    if chol < 200:
        c_flag = "normal"
        c_guide = "Desirable total cholesterol range for adults (< 200 mg/dL)."
    elif chol <= 239:
        c_flag = "borderline_high"
        c_guide = "Borderline high total cholesterol interval (200-239 mg/dL)."
    else:
        c_flag = "high"
        c_guide = "High total cholesterol interval (>= 240 mg/dL), associated with elevated cardiovascular risk."

    return [
        {
            "analyte": "glucose",
            "query_marker": "glucose",
            "matched_marker": "Glucose",
            "value": glucose,
            "unit": "mg/dL",
            "found": True,
            "flag": g_flag,
            "reference_range": "70 - 99 mg/dL",
            "context_status": "CONTEXT_NOT_CONFIRMED",
            "context_qualifier": "Fasting blood glucose reference interval for adults. Fasting duration was not recorded.",
            "educational_guidance": g_guide,
            "citation": "American Diabetes Association (ADA) Standards of Care 2024",
        },
        {
            "analyte": "haemoglobin",
            "query_marker": "haemoglobin",
            "matched_marker": "Hemoglobin",
            "value": hb,
            "unit": "g/dL",
            "found": True,
            "flag": h_flag,
            "reference_range": "12.0 - 17.5 g/dL",
            "context_status": "CONTEXT_NOT_CONFIRMED",
            "context_qualifier": "Adult conventional reference interval. Biological sex not recorded; ranges differ slightly by sex.",
            "educational_guidance": h_guide,
            "citation": "World Health Organization (WHO) Nutritional Anemias Guide",
        },
        {
            "analyte": "cholesterol",
            "query_marker": "cholesterol",
            "matched_marker": "Total Cholesterol",
            "value": chol,
            "unit": "mg/dL",
            "found": True,
            "flag": c_flag,
            "reference_range": "< 200 mg/dL",
            "context_status": "CONTEXT_NOT_CONFIRMED",
            "context_qualifier": "Adult lipid panel guideline reference range for total serum cholesterol.",
            "educational_guidance": c_guide,
            "citation": "National Cholesterol Education Program (NCEP) ATP III",
        },
    ]


def build_ai_remarks(name: str, glucose: float, hb: float, chol: float) -> str:
    """Generate synthesized AI remarks matching the Ollama llama3.2:3b prompt style."""
    abnormalities = []
    if glucose > 99 or glucose < 70:
        abnormalities.append(f"Glucose ({glucose} mg/dL)")
    if hb < 12.0 or hb > 17.5:
        abnormalities.append(f"Haemoglobin ({hb} g/dL)")
    if chol >= 200:
        abnormalities.append(f"Total Cholesterol ({chol} mg/dL)")

    if not abnormalities:
        return (
            f"Laboratory observations for Glucose ({glucose} mg/dL), Haemoglobin ({hb} g/dL), and Total Cholesterol ({chol} mg/dL) "
            "all fall within conventional adult reference intervals. Clinical qualifiers such as fasting duration were unconfirmed. "
            "This automated synthesis is provided for educational demonstration purposes and does not substitute for a clinical consultation."
        )
    else:
        abn_text = ", ".join(abnormalities)
        return (
            f"Laboratory evaluation identifies atypical findings for {abn_text}. "
            "These measurements deviate from standard adult reference intervals. Note that specific clinical context (such as fasting state "
            "and specimen timing) was not recorded at intake. Consultation with a certified medical practitioner is recommended "
            "for diagnostic evaluation. This summary is generated from external reference catalog observations."
        )


DEMO_PATIENTS = [
    {
        "full_name": "Sarah Jenkins",
        "date_of_birth": date(1985, 5, 12),
        "email": "sarah.jenkins@healthmail.test",
        "glucose_value": Decimal("95.000"),
        "haemoglobin_value": Decimal("14.200"),
        "cholesterol_value": Decimal("185.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #1: Normal reference profile",
    },
    {
        "full_name": "Michael Chang",
        "date_of_birth": date(1978, 11, 20),
        "email": "michael.chang@clinical.test",
        "glucose_value": Decimal("240.000"),
        "haemoglobin_value": Decimal("10.200"),
        "cholesterol_value": Decimal("310.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #3: Elevated clinical readings (valid syntax)",
    },
    {
        "full_name": "Emily Davis",
        "date_of_birth": date(1995, 7, 4),
        "email": "emily.davis@mednet.test",
        "glucose_value": Decimal("90.000"),
        "haemoglobin_value": Decimal("14.800"),
        "cholesterol_value": Decimal("160.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #5: Healthy baseline profile",
    },
    {
        "full_name": "Sarah Jenkins",
        "date_of_birth": date(1985, 5, 12),
        "email": "sarah.jenkins@healthmail.test",
        "glucose_value": Decimal("95.000"),
        "haemoglobin_value": Decimal("14.200"),
        "cholesterol_value": Decimal("185.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #6: Confirmed exact duplicate (allow_duplicate=true)",
    },
    {
        "full_name": "Robert Wilson",
        "date_of_birth": date(1968, 9, 18),
        "email": "robert.wilson@partnerhealth.test",
        "glucose_value": Decimal("105.000"),
        "haemoglobin_value": Decimal("13.900"),
        "cholesterol_value": Decimal("225.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #7: Impaired glucose & borderline cholesterol",
    },
    {
        "full_name": "Elena Rostova",
        "date_of_birth": date(1982, 11, 30),
        "email": "elena.rostova@labinsight.test",
        "glucose_value": Decimal("98.000"),
        "haemoglobin_value": Decimal("14.500"),
        "cholesterol_value": Decimal("195.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #9: Valid calendar boundary test (Nov 30)",
    },
    {
        "full_name": "James Thorne",
        "date_of_birth": date(1992, 4, 25),
        "email": "james.thorne@careprovider.test",
        "glucose_value": Decimal("85.000"),
        "haemoglobin_value": Decimal("15.200"),
        "cholesterol_value": Decimal("170.000"),
        "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
        "note": "Assessment Submission #10: Valid registration candidate for cascade deletion",
    },
]


def seed_database(reset: bool = False) -> None:
    """Seed the database with assessment demo records."""
    factory = SessionLocal

    with factory() as db:
        existing_count = db.scalar(select(func.count(Patient.id))) or 0
        if existing_count > 0:
            if not reset:
                print(f"[!] Database already contains {existing_count} patient records.")
                print("    Use 'python scripts/seed_demo_data.py --reset' to clear and re-seed.")
                return
            else:
                print(f"[-] Reset requested: Removing {existing_count} existing patient records...")
                db.execute(delete(Patient))
                db.commit()

        print(
            "[+] Seeding 7 demonstration patient records with TestWell observations and AI remarks..."
        )

        now = datetime.now(UTC)

        for p_data in DEMO_PATIENTS:
            p_data.pop("note", None)
            patient = Patient(**p_data, created_at=now, updated_at=now)
            db.add(patient)
            db.flush()

            # Generate realistic TestWell observation output
            g_float = float(patient.glucose_value)
            h_float = float(patient.haemoglobin_value)
            c_float = float(patient.cholesterol_value)

            observations = build_observations(g_float, h_float, c_float)
            ai_text = build_ai_remarks(patient.full_name, g_float, h_float, c_float)

            snapshot = {
                "glucose": {"value": g_float, "unit": "mg/dL"},
                "haemoglobin": {"value": h_float, "unit": "g/dL"},
                "cholesterol": {"value": c_float, "unit": "mg/dL"},
                "unit_profile_code": "ASSESSMENT_CONVENTIONAL_V1",
            }

            provider_result = {
                "provider": "testwell",
                "api_version": "v1.0",
                "observations": observations,
                "summary": {
                    "total": 3,
                    "matched": 3,
                    "normal": sum(1 for o in observations if o["flag"] == "normal"),
                    "abnormal": sum(1 for o in observations if o["flag"] != "normal"),
                },
            }

            ai_result = {
                "summary": ai_text,
                "generation_label": "AI_GENERATED",
                "model": "llama3.2:3b",
                "safety_passed": True,
            }

            analysis = PatientAnalysis(
                patient_id=patient.id,
                run_number=1,
                input_snapshot_json=snapshot,
                external_provider="testwell",
                external_api_version="v1.0",
                external_status=ExternalStatus.SUCCEEDED,
                external_result_json=provider_result,
                ai_provider="ollama",
                ai_model="llama3.2:3b",
                ai_status=AiStatus.SUCCEEDED,
                ai_result_json=ai_result,
                remarks_text=ai_text,
                overall_status=OverallStatus.COMPLETED,
                ruleset_version="testwell-normalizer-v1",
                prompt_version="labinsight-v1",
                created_at=now,
                started_at=now,
                completed_at=now,
            )
            db.add(analysis)

        db.commit()

        print("\n[SUCCESS] Successfully seeded 7 demonstration records into database:")
        print(
            "---------------------------------------------------------------------------------------------------------"
        )
        print(
            f"{'ID':<4} | {'Name':<16} | {'DOB':<10} | {'Email':<30} | {'Gluc':<6} | {'Hb':<5} | {'Chol':<5}"
        )
        print(
            "---------------------------------------------------------------------------------------------------------"
        )
        patients = db.scalars(select(Patient).order_by(Patient.id.asc())).all()
        for p in patients:
            print(
                f"{p.id:<4} | {p.full_name:<16} | {p.date_of_birth.strftime('%d/%m/%Y'):<10} | "
                f"{p.email:<30} | {p.glucose_value:<6} | {p.haemoglobin_value:<5} | {p.cholesterol_value:<5}"
            )
        print(
            "---------------------------------------------------------------------------------------------------------"
        )
        print(
            "You can now open the dashboard (http://127.0.0.1:5173/) to present the populated prototype!"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed LabInsight demonstration data.")
    parser.add_argument(
        "--reset", action="store_true", help="Clear existing records before seeding."
    )
    args = parser.parse_args()
    seed_database(reset=args.reset)
