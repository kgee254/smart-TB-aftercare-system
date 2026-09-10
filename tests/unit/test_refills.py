import pytest
from datetime import date

from app.refills import RefillManager


@pytest.fixture
def refill_manager():
    return RefillManager(
        patient_id=1,
        medication_id=201,
        quantity=180,
        frequency=1,
        start_date=date(2026, 9, 10)
    )


def test_create_refill_manager(refill_manager):
    assert refill_manager.patient_id == 1
    assert refill_manager.medication_id == 201
    assert refill_manager.quantity == 180
    assert refill_manager.frequency == 1
    assert refill_manager.start_date == date(2026, 9, 10)


def test_remaining_quantity_is_calculated(refill_manager):
    remaining = refill_manager.calculate_remaining_quantity(
        doses_taken=50
    )

    assert remaining == 130


def test_remaining_quantity_cannot_be_negative(refill_manager):
    remaining = refill_manager.calculate_remaining_quantity(
        doses_taken=200
    )

    assert remaining == 0


def test_low_medication_threshold_is_detected(refill_manager):
    is_low = refill_manager.is_supply_low(
        remaining_quantity=20,
        threshold=30
    )

    assert is_low is True


def test_medication_above_threshold_is_not_low(refill_manager):
    is_low = refill_manager.is_supply_low(
        remaining_quantity=50,
        threshold=30
    )

    assert is_low is False


def test_low_medication_alert_can_be_created(refill_manager):
    alert = refill_manager.create_alert(
        remaining_quantity=20,
        threshold=30
    )

    assert alert["patient_id"] == 1
    assert alert["medication_id"] == 201
    assert alert["remaining_quantity"] == 20
    assert alert["threshold"] == 30
    assert alert["status"] == "active"


def test_alert_is_not_created_when_supply_is_not_low(refill_manager):
    alert = refill_manager.create_alert(
        remaining_quantity=50,
        threshold=30
    )

    assert alert is None


def test_patient_can_request_refill(refill_manager):
    request = refill_manager.request_refill()

    assert request["patient_id"] == 1
    assert request["medication_id"] == 201
    assert request["status"] == "requested"


def test_refill_request_can_be_updated(refill_manager):
    request = refill_manager.request_refill()

    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="in_progress"
    )

    updated_request = refill_manager.get_request(
        request["request_id"]
    )

    assert updated_request["status"] == "in_progress"


def test_refill_request_can_be_completed(refill_manager):
    request = refill_manager.request_refill()

    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="completed"
    )

    updated_request = refill_manager.get_request(
        request["request_id"]
    )

    assert updated_request["status"] == "completed"


def test_invalid_refill_request_status_is_rejected(refill_manager):
    request = refill_manager.request_refill()

    with pytest.raises(ValueError):
        refill_manager.update_request_status(
            request_id=request["request_id"],
            status="invalid"
        )


def test_duplicate_active_refill_request_is_rejected(refill_manager):
    refill_manager.request_refill()

    with pytest.raises(ValueError):
        refill_manager.request_refill()


def test_refill_manager_requires_patient():
    with pytest.raises(ValueError):
        RefillManager(
            patient_id=None,
            medication_id=201,
            quantity=180,
            frequency=1,
            start_date=date(2026, 9, 10)
        )


def test_refill_manager_requires_medication():
    with pytest.raises(ValueError):
        RefillManager(
            patient_id=1,
            medication_id=None,
            quantity=180,
            frequency=1,
            start_date=date(2026, 9, 10)
        )


def test_medication_quantity_must_be_positive():
    with pytest.raises(ValueError):
        RefillManager(
            patient_id=1,
            medication_id=201,
            quantity=0,
            frequency=1,
            start_date=date(2026, 9, 10)
        )


def test_medication_frequency_must_be_positive():
    with pytest.raises(ValueError):
        RefillManager(
            patient_id=1,
            medication_id=201,
            quantity=180,
            frequency=0,
            start_date=date(2026, 9, 10)
        )