import pytest
from datetime import date

from app.adherence import AdherenceTracker


@pytest.fixture
def adherence_tracker():
    return AdherenceTracker(
        patient_id=1,
        medication_id=201
    )


def test_create_adherence_tracker(adherence_tracker):
    assert adherence_tracker.patient_id == 1
    assert adherence_tracker.medication_id == 201


def test_new_adherence_tracker_has_no_records(adherence_tracker):
    assert adherence_tracker.get_history() == []


def test_record_taken_dose(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    history = adherence_tracker.get_history()

    assert len(history) == 1
    assert history[0]["date"] == date(2026, 9, 10)
    assert history[0]["status"] == "taken"


def test_record_missed_dose(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 11),
        status="missed"
    )

    history = adherence_tracker.get_history()

    assert len(history) == 1
    assert history[0]["date"] == date(2026, 9, 11)
    assert history[0]["status"] == "missed"


def test_multiple_doses_can_be_recorded(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 11),
        status="taken"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 12),
        status="missed"
    )

    history = adherence_tracker.get_history()

    assert len(history) == 3


def test_invalid_adherence_status_is_rejected(adherence_tracker):
    with pytest.raises(ValueError):
        adherence_tracker.record_dose(
            dose_date=date(2026, 9, 10),
            status="maybe"
        )


def test_adherence_percentage_is_calculated(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 11),
        status="taken"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 12),
        status="missed"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 13),
        status="taken"
    )

    assert adherence_tracker.get_adherence_percentage() == 75.0


def test_all_taken_doses_give_100_percent_adherence(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 11),
        status="taken"
    )

    assert adherence_tracker.get_adherence_percentage() == 100.0


def test_no_recorded_doses_give_zero_adherence(adherence_tracker):
    assert adherence_tracker.get_adherence_percentage() == 0.0


def test_missed_dose_count_is_calculated(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 11),
        status="missed"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 12),
        status="missed"
    )

    assert adherence_tracker.get_missed_dose_count() == 2


def test_duplicate_dose_date_is_rejected(adherence_tracker):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    with pytest.raises(ValueError):
        adherence_tracker.record_dose(
            dose_date=date(2026, 9, 10),
            status="missed"
        )


def test_adherence_tracker_requires_patient(adherence_tracker):
    with pytest.raises(ValueError):
        AdherenceTracker(
            patient_id=None,
            medication_id=201
        )


def test_adherence_tracker_requires_medication(adherence_tracker):
    with pytest.raises(ValueError):
        AdherenceTracker(
            patient_id=1,
            medication_id=None
        )