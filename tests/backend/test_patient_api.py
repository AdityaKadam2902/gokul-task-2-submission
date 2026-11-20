"""Integration tests for Patient and Analysis REST API endpoints.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from decimal import Decimal

from app.models.patient import Patient
from app.models.patient_analysis import PatientAnalysis
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_create_patient_success(api_client: TestClient) -> None:
    """Test successful patient creation returns 201 and initial PENDING analysis."""
    payload = {
        "full_name": "Taylor Intake",
        "date_of_birth": "12/04/1991",
        "email": "taylor.intake@example.test",
        "glucose_value": 92.5,
        "haemoglobin_value": 14.1,
        "cholesterol_value": 182.0,
    }
    response = api_client.post("/api/v1/patients", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["full_name"] == "Taylor Intake"
    assert data["date_of_birth"] == "1991-04-12"
    assert data["email"] == "taylor.intake@example.test"
    assert Decimal(str(data["glucose_value"])) == Decimal("92.5")
    assert Decimal(str(data["haemoglobin_value"])) == Decimal("14.1")
    assert Decimal(str(data["cholesterol_value"])) == Decimal("182.0")
    assert data["latest_analysis"] is not None
    assert data["latest_analysis"]["run_number"] == 1
    assert data["latest_analysis"]["overall_status"] == "PENDING"
    assert data["latest_analysis"]["external_status"] == "PENDING"
    assert data["latest_analysis"]["ai_status"] == "NOT_RUN"


def test_create_patient_validation_error_envelope(api_client: TestClient) -> None:
    """Verify validation errors return HTTP 422 with the documented standard error envelope."""
    payload = {
        "full_name": "",  # Empty name
        "date_of_birth": "32/01/1990",  # Impossible calendar date
        "email": "not-an-email",  # Malformed email
        "glucose_value": -10.0,  # Negative value
        "haemoglobin_value": 14.0,
        "cholesterol_value": 180.0,
    }
    response = api_client.post("/api/v1/patients", json=payload)
    assert response.status_code == 422

    body = response.json()
    assert "error" in body
    err = body["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "request_id" in err
    assert len(err["details"]) >= 3


def test_duplicate_confirmation_workflow(api_client: TestClient) -> None:
    """Test full duplicate detection, 409 conflict, and confirmed second insertion."""
    patient_payload = {
        "full_name": "Jordan Duplicate",
        "date_of_birth": "15.08.1989",
        "email": "jordan.dup@example.test",
        "glucose_value": 94.0,
        "haemoglobin_value": 13.8,
        "cholesterol_value": 178.0,
    }

    # 1. First submission succeeds (201 Created)
    r1 = api_client.post("/api/v1/patients", json=patient_payload)
    assert r1.status_code == 201
    patient1_id = r1.json()["id"]

    # 2. Second exact submission without allow_duplicate returns HTTP 409 Conflict
    r2 = api_client.post("/api/v1/patients", json=patient_payload)
    assert r2.status_code == 409
    err = r2.json()["error"]
    assert err["code"] == "DUPLICATE_RECORD"
    assert err["existing_patient_id"] == patient1_id
    assert "Confirm to proceed" in err["message"]

    # 3. Third submission with allow_duplicate=true confirms insertion and returns 201 Created
    confirmed_payload = {**patient_payload, "allow_duplicate": True}
    r3 = api_client.post("/api/v1/patients", json=confirmed_payload)
    assert r3.status_code == 201
    patient2_id = r3.json()["id"]
    assert patient2_id != patient1_id

    # Verify both records exist in list
    list_res = api_client.get("/api/v1/patients")
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 2


def test_list_patients_pagination_and_ordering(api_client: TestClient) -> None:
    """Test patient listing, pagination, and stable ordering."""
    for i in range(5):
        api_client.post(
            "/api/v1/patients",
            json={
                "full_name": f"Patient Number {i}",
                "date_of_birth": f"01/01/199{i}",
                "email": f"patient{i}@example.test",
                "glucose_value": 90.0 + i,
                "haemoglobin_value": 14.0,
                "cholesterol_value": 180.0,
            },
        )

    # Page 1 with page_size=2
    res = api_client.get("/api/v1/patients?page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 5
    assert data["total_pages"] == 3
    assert len(data["items"]) == 2
    # Verify newest first (created_at DESC, id DESC)
    assert data["items"][0]["full_name"] == "Patient Number 4"
    assert data["items"][1]["full_name"] == "Patient Number 3"


def test_list_patients_search_filter(api_client: TestClient) -> None:
    """Test searching patient list by name or email substring."""
    api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Alice Findme",
            "date_of_birth": "10/02/1985",
            "email": "alice@searchtest.com",
            "glucose_value": 90.0,
            "haemoglobin_value": 14.0,
            "cholesterol_value": 180.0,
        },
    )
    api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Bob Other",
            "date_of_birth": "11/03/1986",
            "email": "bob@other.com",
            "glucose_value": 95.0,
            "haemoglobin_value": 14.5,
            "cholesterol_value": 185.0,
        },
    )

    search_res = api_client.get("/api/v1/patients?search=Findme")
    assert search_res.status_code == 200
    items = search_res.json()["items"]
    assert len(items) == 1
    assert items[0]["full_name"] == "Alice Findme"


def test_get_patient_by_id_and_not_found(api_client: TestClient) -> None:
    """Test retrieving existing patient and 404 for unknown ID."""
    create_res = api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Morgan Detail",
            "date_of_birth": "14/07/1992",
            "email": "morgan@detail.test",
            "glucose_value": 91.0,
            "haemoglobin_value": 13.9,
            "cholesterol_value": 179.0,
        },
    )
    p_id = create_res.json()["id"]

    # Found
    get_res = api_client.get(f"/api/v1/patients/{p_id}")
    assert get_res.status_code == 200
    assert get_res.json()["full_name"] == "Morgan Detail"

    # Not found
    not_found = api_client.get("/api/v1/patients/999999")
    assert not_found.status_code == 404
    assert not_found.json()["error"]["code"] == "NOT_FOUND"


def test_patch_patient_email_only_preserves_analysis(api_client: TestClient) -> None:
    """Updating email to gokul@infocare.com must succeed without creating a new analysis run."""
    create_res = api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Casey EmailTest",
            "date_of_birth": "20/09/1987",
            "email": "old.email@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 14.0,
            "cholesterol_value": 180.0,
        },
    )
    p_id = create_res.json()["id"]

    # PATCH email to gokul@infocare.com
    patch_res = api_client.patch(
        f"/api/v1/patients/{p_id}",
        json={"email": "gokul@infocare.com"},
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["email"] == "gokul@infocare.com"
    # Remains run_number 1
    assert updated["latest_analysis"]["run_number"] == 1

    # Verify analysis count is still 1
    history_res = api_client.get(f"/api/v1/patients/{p_id}/analyses")
    assert len(history_res.json()) == 1


def test_patch_patient_measurement_change_creates_new_analysis(
    api_client: TestClient,
) -> None:
    """Updating clinical measurements creates a fresh PENDING analysis run in history."""
    create_res = api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Reanalysis Test",
            "date_of_birth": "18/11/1990",
            "email": "reanalysis@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 14.0,
            "cholesterol_value": 180.0,
        },
    )
    p_id = create_res.json()["id"]

    # PATCH glucose measurement
    patch_res = api_client.patch(
        f"/api/v1/patients/{p_id}",
        json={"glucose_value": 115.5},
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert Decimal(str(updated["glucose_value"])) == Decimal("115.5")
    assert updated["latest_analysis"]["run_number"] == 2
    assert updated["latest_analysis"]["overall_status"] == "PENDING"

    # History now contains 2 runs
    history_res = api_client.get(f"/api/v1/patients/{p_id}/analyses")
    runs = history_res.json()
    assert len(runs) == 2
    assert runs[0]["run_number"] == 2
    assert runs[1]["run_number"] == 1


def test_patch_patient_self_update_does_not_conflict(api_client: TestClient) -> None:
    """Updating a patient with unchanged values does not falsely conflict with itself."""
    create_res = api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Self Conflict Test",
            "date_of_birth": "22/03/1993",
            "email": "self@example.test",
            "glucose_value": 92.0,
            "haemoglobin_value": 13.8,
            "cholesterol_value": 175.0,
        },
    )
    p_id = create_res.json()["id"]

    # Patch with same email
    patch_res = api_client.patch(
        f"/api/v1/patients/{p_id}",
        json={"email": "self@example.test"},
    )
    assert patch_res.status_code == 200


def test_patch_patient_conflicting_with_other_record(api_client: TestClient) -> None:
    """Updating patient to match another record triggers 409 Conflict without allow_duplicate."""
    # Create patient A
    api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Record A",
            "date_of_birth": "05/05/1990",
            "email": "record.a@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 14.0,
            "cholesterol_value": 180.0,
        },
    )
    # Create patient B
    p_b = api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Record B",
            "date_of_birth": "06/06/1991",
            "email": "record.b@example.test",
            "glucose_value": 95.0,
            "haemoglobin_value": 14.5,
            "cholesterol_value": 185.0,
        },
    ).json()

    # Try updating Record B to match Record A exactly
    conflict_res = api_client.patch(
        f"/api/v1/patients/{p_b['id']}",
        json={
            "full_name": "Record A",
            "date_of_birth": "05/05/1990",
            "email": "record.a@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 14.0,
            "cholesterol_value": 180.0,
        },
    )
    assert conflict_res.status_code == 409
    assert conflict_res.json()["error"]["code"] == "DUPLICATE_RECORD"


def test_delete_patient_and_cascade(api_client: TestClient, test_db_session: Session) -> None:
    """Delete patient returns 204 and cascades deletion to analysis history."""
    create_res = api_client.post(
        "/api/v1/patients",
        json={
            "full_name": "Delete Target",
            "date_of_birth": "19/04/1988",
            "email": "delete.target@example.test",
            "glucose_value": 90.0,
            "haemoglobin_value": 14.0,
            "cholesterol_value": 180.0,
        },
    )
    p_id = create_res.json()["id"]

    # Delete
    del_res = api_client.delete(f"/api/v1/patients/{p_id}")
    assert del_res.status_code == 204

    # Subsequent GET returns 404
    get_res = api_client.get(f"/api/v1/patients/{p_id}")
    assert get_res.status_code == 404

    # Direct database check: patient and analyses are gone
    assert test_db_session.get(Patient, p_id) is None
    analyses = test_db_session.scalars(
        select(PatientAnalysis).where(PatientAnalysis.patient_id == p_id)
    ).all()
    assert len(analyses) == 0


def test_get_analysis_statuses_metadata(api_client: TestClient) -> None:
    """Test metadata discovery endpoint GET /api/v1/meta/analysis-statuses."""
    res = api_client.get("/api/v1/meta/analysis-statuses")
    assert res.status_code == 200
    data = res.json()
    assert "external_status" in data
    assert "ai_status" in data
    assert "overall_status" in data
    assert "PENDING" in data["overall_status"]
    assert "COMPLETED" in data["overall_status"]
    assert "DEGRADED" in data["overall_status"]
