import pytest
from models.refill import RefillRequest


def test_create_refill_request():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    assert refill.request_id == 1
    assert refill.patient_id == 10
    assert refill.medication_id == 20
    assert refill.status == "pending"


def test_approve_refill():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    refill.approve()

    assert refill.status == "approved"


def test_reject_refill():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    refill.reject()

    assert refill.status == "rejected"


def test_complete_refill():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    refill.approve()
    refill.complete()

    assert refill.status == "completed"


def test_cannot_complete_pending_refill():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    with pytest.raises(ValueError):
        refill.complete()


def test_cannot_approve_rejected_refill():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    refill.reject()

    with pytest.raises(ValueError):
        refill.approve()


def test_to_dict():
    refill = RefillRequest(
        request_id=1,
        patient_id=10,
        medication_id=20
    )

    data = refill.to_dict()

    assert data["request_id"] == 1
    assert data["patient_id"] == 10
    assert data["medication_id"] == 20
    assert data["status"] == "pending"


def test_from_dict():
    data = {
        "request_id": 1,
        "patient_id": 10,
        "medication_id": 20,
        "status": "approved",
        "date": "2026-09-12 09:00:00"
    }

    refill = RefillRequest.from_dict(data)

    assert refill.request_id == 1
    assert refill.patient_id == 10
    assert refill.medication_id == 20
    assert refill.status == "approved"