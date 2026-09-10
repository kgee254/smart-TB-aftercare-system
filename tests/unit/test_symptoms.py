import pytest
from datetime import date

from app.symptoms import SymptomTracker


@pytest.fixture
def symptom_tracker():
    return SymptomTracker(patient_id=1)


def test_create_symptom_tracker(symptom_tracker):
    assert symptom_tracker.patient_id == 1


def test_new_symptom_tracker_has_no_records(symptom_tracker):
    assert symptom_tracker.get_history() == []


def test_record_common_symptoms(symptom_tracker):
    symptoms = [
        "cough",
        "fever",
        "night_sweats"
    ]

    record = symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 10),
        symptoms=symptoms
    )

    assert record["patient_id"] == 1
    assert record["date"] == date(2026, 9, 10)
    assert record["symptoms"] == symptoms


def test_record_symptom_checkin_without_symptoms(symptom_tracker):
    record = symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 11),
        symptoms=[]
    )

    assert record["symptoms"] == []


def test_other_symptom_can_be_recorded(symptom_tracker):
    record = symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 12),
        symptoms=["other"],
        other_symptom="Chest discomfort"
    )

    assert record["symptoms"] == ["other"]
    assert record["other_symptom"] == "Chest discomfort"


def test_other_symptom_requires_description(symptom_tracker):
    with pytest.raises(ValueError):
        symptom_tracker.record_checkin(
            checkin_date=date(2026, 9, 12),
            symptoms=["other"]
        )


def test_invalid_symptom_is_rejected(symptom_tracker):
    with pytest.raises(ValueError):
        symptom_tracker.record_checkin(
            checkin_date=date(2026, 9, 13),
            symptoms=["unknown_symptom"]
        )


def test_symptom_severity_can_be_recorded(symptom_tracker):
    record = symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 14),
        symptoms=["cough"],
        severity="moderate"
    )

    assert record["severity"] == "moderate"


def test_invalid_symptom_severity_is_rejected(symptom_tracker):
    with pytest.raises(ValueError):
        symptom_tracker.record_checkin(
            checkin_date=date(2026, 9, 14),
            symptoms=["cough"],
            severity="extreme"
        )


def test_notes_can_be_added_to_symptom_checkin(symptom_tracker):
    record = symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 15),
        symptoms=["fatigue"],
        notes="Patient feels tired after taking medication."
    )

    assert record["notes"] == (
        "Patient feels tired after taking medication."
    )


def test_multiple_symptom_checkins_can_be_recorded(symptom_tracker):
    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 10),
        symptoms=["cough"]
    )

    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 11),
        symptoms=["cough", "fever"]
    )

    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 12),
        symptoms=[]
    )

    history = symptom_tracker.get_history()

    assert len(history) == 3


def test_symptom_history_is_returned(symptom_tracker):
    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 10),
        symptoms=["cough"]
    )

    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 11),
        symptoms=["fever", "night_sweats"]
    )

    history = symptom_tracker.get_history()

    assert history[0]["date"] == date(2026, 9, 10)
    assert history[0]["symptoms"] == ["cough"]

    assert history[1]["date"] == date(2026, 9, 11)
    assert history[1]["symptoms"] == [
        "fever",
        "night_sweats"
    ]


def test_duplicate_checkin_date_is_rejected(symptom_tracker):
    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 10),
        symptoms=["cough"]
    )

    with pytest.raises(ValueError):
        symptom_tracker.record_checkin(
            checkin_date=date(2026, 9, 10),
            symptoms=["fever"]
        )


def test_patient_id_is_required():
    with pytest.raises(ValueError):
        SymptomTracker(patient_id=None)