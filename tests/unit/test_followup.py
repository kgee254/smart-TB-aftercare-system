import pytest
from datetime import date

from app.followup import FollowUpTracker


@pytest.fixture
def followup_tracker():
    return FollowUpTracker(healthworker_id=1)


def test_create_followup_tracker(followup_tracker):
    assert followup_tracker.healthworker_id == 1


def test_new_followup_tracker_has_no_cases(followup_tracker):
    assert followup_tracker.get_cases() == []


def test_create_followup_case(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Low medication adherence"
    )

    assert case["patient_id"] == 2
    assert case["healthworker_id"] == 1
    assert case["reason"] == "Low medication adherence"
    assert case["status"] == "open"


def test_followup_case_has_creation_date(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Missed medication doses"
    )

    assert case["created_date"] == date.today()


def test_followup_case_can_be_updated(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Low medication adherence"
    )

    followup_tracker.update_case(
        case_id=case["case_id"],
        action="Called patient to discuss missed doses."
    )

    updated_case = followup_tracker.get_case(case["case_id"])

    assert updated_case["action"] == (
        "Called patient to discuss missed doses."
    )


def test_followup_case_status_can_be_updated(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Low medication adherence"
    )

    followup_tracker.update_status(
        case_id=case["case_id"],
        status="in_progress"
    )

    updated_case = followup_tracker.get_case(case["case_id"])

    assert updated_case["status"] == "in_progress"


def test_followup_case_can_be_completed(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Missed medication doses"
    )

    followup_tracker.update_status(
        case_id=case["case_id"],
        status="completed"
    )

    updated_case = followup_tracker.get_case(case["case_id"])

    assert updated_case["status"] == "completed"


def test_invalid_followup_status_is_rejected(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Low medication adherence"
    )

    with pytest.raises(ValueError):
        followup_tracker.update_status(
            case_id=case["case_id"],
            status="invalid"
        )


def test_healthworker_can_view_patient_followup_cases(followup_tracker):
    followup_tracker.create_case(
        patient_id=2,
        reason="Low medication adherence"
    )

    followup_tracker.create_case(
        patient_id=2,
        reason="Patient reported symptoms"
    )

    followup_tracker.create_case(
        patient_id=3,
        reason="Missed medication doses"
    )

    cases = followup_tracker.get_patient_cases(patient_id=2)

    assert len(cases) == 2

    assert cases[0]["patient_id"] == 2
    assert cases[1]["patient_id"] == 2


def test_healthworker_can_view_open_cases(followup_tracker):
    case1 = followup_tracker.create_case(
        patient_id=2,
        reason="Low medication adherence"
    )

    case2 = followup_tracker.create_case(
        patient_id=3,
        reason="Patient reported symptoms"
    )

    followup_tracker.update_status(
        case_id=case1["case_id"],
        status="completed"
    )

    open_cases = followup_tracker.get_open_cases()

    assert len(open_cases) == 1
    assert open_cases[0]["case_id"] == case2["case_id"]


def test_followup_case_can_be_escalated(followup_tracker):
    case = followup_tracker.create_case(
        patient_id=2,
        reason="Patient symptoms worsening"
    )

    followup_tracker.escalate_case(
        case_id=case["case_id"],
        reason="Patient requires doctor review."
    )

    updated_case = followup_tracker.get_case(case["case_id"])

    assert updated_case["status"] == "escalated"
    assert updated_case["escalation_reason"] == (
        "Patient requires doctor review."
    )


def test_followup_case_requires_patient(followup_tracker):
    with pytest.raises(ValueError):
        followup_tracker.create_case(
            patient_id=None,
            reason="Low medication adherence"
        )


def test_followup_case_requires_reason(followup_tracker):
    with pytest.raises(ValueError):
        followup_tracker.create_case(
            patient_id=2,
            reason=""
        )


def test_healthworker_is_required():
    with pytest.raises(ValueError):
        FollowUpTracker(healthworker_id=None)