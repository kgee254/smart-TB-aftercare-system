import pytest
from datetime import date, timedelta

from app.treatment import Treatment


@pytest.fixture
def treatment():
    return Treatment(
        treatment_id=101,
        patient_id=1,
        start_date=date(2026, 9, 10),
        duration_days=180,
        instructions="Take medication according to the prescription."
    )


def test_create_treatment(treatment):
    assert treatment.treatment_id == 101
    assert treatment.patient_id == 1
    assert treatment.start_date == date(2026, 9, 10)
    assert treatment.duration_days == 180
    assert treatment.instructions == (
        "Take medication according to the prescription."
    )


def test_new_treatment_is_active(treatment):
    assert treatment.status == "active"


def test_get_treatment_details(treatment):
    details = treatment.get_details()

    assert details["treatment_id"] == 101
    assert details["patient_id"] == 1
    assert details["start_date"] == date(2026, 9, 10)
    assert details["duration_days"] == 180
    assert details["status"] == "active"


def test_treatment_end_date_is_calculated(treatment):
    expected_end_date = date(2026, 9, 10) + timedelta(days=180)

    assert treatment.get_end_date() == expected_end_date


def test_treatment_status_can_be_updated(treatment):
    treatment.update_status("completed")

    assert treatment.status == "completed"


def test_invalid_treatment_status_is_rejected(treatment):
    with pytest.raises(ValueError):
        treatment.update_status("invalid")


def test_treatment_duration_must_be_positive():
    with pytest.raises(ValueError):
        Treatment(
            treatment_id=101,
            patient_id=1,
            start_date=date(2026, 9, 10),
            duration_days=0,
            instructions="Take medication according to the prescription."
        )


def test_treatment_instructions_can_be_updated(treatment):
    new_instructions = "Take medication after meals."

    treatment.update_instructions(new_instructions)

    assert treatment.instructions == new_instructions


def test_treatment_must_belong_to_a_patient():
    with pytest.raises(ValueError):
        Treatment(
            treatment_id=101,
            patient_id=None,
            start_date=date(2026, 9, 10),
            duration_days=180,
            instructions="Take medication according to the prescription."
        )