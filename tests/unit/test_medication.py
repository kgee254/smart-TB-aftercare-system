import pytest

from app.medication import Medication


@pytest.fixture
def medication():
    return Medication(
        medication_id=201,
        treatment_id=101,
        name="Rifampicin",
        dosage=600,
        frequency=1,
        quantity=180,
        duration_days=180,
        instructions="Take once daily."
    )


def test_create_medication(medication):
    assert medication.medication_id == 201
    assert medication.treatment_id == 101
    assert medication.name == "Rifampicin"
    assert medication.dosage == 600
    assert medication.frequency == 1
    assert medication.quantity == 180
    assert medication.duration_days == 180
    assert medication.instructions == "Take once daily."


def test_medication_details_are_stored_correctly(medication):
    assert medication.name == "Rifampicin"
    assert medication.dosage == 600
    assert medication.frequency == 1
    assert medication.quantity == 180


def test_get_medication_details(medication):
    details = medication.get_details()

    assert details["medication_id"] == 201
    assert details["treatment_id"] == 101
    assert details["name"] == "Rifampicin"
    assert details["dosage"] == 600
    assert details["frequency"] == 1
    assert details["quantity"] == 180
    assert details["duration_days"] == 180
    assert details["instructions"] == "Take once daily."


def test_dosage_must_be_positive():
    with pytest.raises(ValueError):
        Medication(
            medication_id=201,
            treatment_id=101,
            name="Rifampicin",
            dosage=0,
            frequency=1,
            quantity=180,
            duration_days=180,
            instructions="Take once daily."
        )


def test_quantity_must_be_positive():
    with pytest.raises(ValueError):
        Medication(
            medication_id=201,
            treatment_id=101,
            name="Rifampicin",
            dosage=600,
            frequency=1,
            quantity=0,
            duration_days=180,
            instructions="Take once daily."
        )


def test_frequency_must_be_positive():
    with pytest.raises(ValueError):
        Medication(
            medication_id=201,
            treatment_id=101,
            name="Rifampicin",
            dosage=600,
            frequency=0,
            quantity=180,
            duration_days=180,
            instructions="Take once daily."
        )


def test_duration_must_be_positive():
    with pytest.raises(ValueError):
        Medication(
            medication_id=201,
            treatment_id=101,
            name="Rifampicin",
            dosage=600,
            frequency=1,
            quantity=180,
            duration_days=0,
            instructions="Take once daily."
        )


def test_medication_must_belong_to_treatment():
    with pytest.raises(ValueError):
        Medication(
            medication_id=201,
            treatment_id=None,
            name="Rifampicin",
            dosage=600,
            frequency=1,
            quantity=180,
            duration_days=180,
            instructions="Take once daily."
        )


def test_medication_instructions_can_be_updated(medication):
    medication.update_instructions("Take once daily after food.")

    assert medication.instructions == "Take once daily after food."


def test_remaining_quantity_can_be_calculated(medication):
    medication.record_dose()

    assert medication.get_remaining_quantity() == 179


def test_remaining_quantity_cannot_be_negative(medication):
    for _ in range(180):
        medication.record_dose()

    assert medication.get_remaining_quantity() == 0