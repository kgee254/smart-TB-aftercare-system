import pytest
from datetime import date

from app.patient import Patient
from app.doctor import Doctor
from app.healthworker import HealthWorker
from app.treatment import Treatment
from app.medication import Medication
from app.refills import RefillManager


@pytest.fixture
def patient():
    return Patient(
        patient_id=1,
        name="John Kamau",
        username="john1",
        password="john123",
        phone="0711111111"
    )


@pytest.fixture
def doctor():
    return Doctor(
        doctor_id=1,
        name="Dr. Jane Wanjiku",
        username="doctor1",
        password="doctor123",
        phone="0712345678",
        specialization="TB Specialist"
    )


@pytest.fixture
def healthworker():
    return HealthWorker(
        healthworker_id=1,
        name="Grace Wambui",
        username="healthworker1",
        password="health123",
        phone="0733333333"
    )


@pytest.fixture
def treatment(patient):
    return Treatment(
        treatment_id=101,
        patient_id=patient.patient_id,
        start_date=date(2026, 9, 10),
        duration_days=180,
        instructions="Take medication according to the prescription."
    )


@pytest.fixture
def medication(treatment):
    return Medication(
        medication_id=201,
        treatment_id=treatment.treatment_id,
        name="Rifampicin",
        dosage=600,
        frequency=1,
        quantity=180,
        duration_days=180,
        instructions="Take once daily."
    )


@pytest.fixture
def refill_manager(patient, medication):
    return RefillManager(
        patient_id=patient.patient_id,
        medication_id=medication.medication_id,
        quantity=medication.quantity,
        frequency=medication.frequency,
        start_date=date(2026, 9, 10)
    )


def test_medication_supply_belongs_to_correct_patient_and_treatment(
    patient,
    treatment,
    medication,
    refill_manager
):
    assert treatment.patient_id == patient.patient_id
    assert medication.treatment_id == treatment.treatment_id
    assert refill_manager.patient_id == patient.patient_id
    assert refill_manager.medication_id == medication.medication_id


def test_remaining_medication_supply_can_be_calculated(
    medication,
    refill_manager
):
    doses_taken = 150

    remaining = refill_manager.calculate_remaining_quantity(
        doses_taken=doses_taken
    )

    assert remaining == 30
    assert medication.quantity == 180


def test_system_detects_low_medication_supply(
    refill_manager
):
    remaining_quantity = refill_manager.calculate_remaining_quantity(
        doses_taken=160
    )

    assert remaining_quantity == 20

    assert refill_manager.is_supply_low(
        remaining_quantity=remaining_quantity,
        threshold=30
    ) is True


def test_system_creates_low_medication_alert(
    patient,
    medication,
    refill_manager
):
    remaining_quantity = refill_manager.calculate_remaining_quantity(
        doses_taken=160
    )

    alert = refill_manager.create_alert(
        remaining_quantity=remaining_quantity,
        threshold=30
    )

    assert alert is not None
    assert alert["patient_id"] == patient.patient_id
    assert alert["medication_id"] == medication.medication_id
    assert alert["remaining_quantity"] == 20
    assert alert["threshold"] == 30
    assert alert["status"] == "active"


def test_no_alert_is_created_when_medication_supply_is_sufficient(
    refill_manager
):
    remaining_quantity = refill_manager.calculate_remaining_quantity(
        doses_taken=100
    )

    alert = refill_manager.create_alert(
        remaining_quantity=remaining_quantity,
        threshold=30
    )

    assert remaining_quantity == 80
    assert alert is None


def test_patient_can_request_refill_when_supply_is_low(
    patient,
    medication,
    refill_manager
):
    remaining_quantity = refill_manager.calculate_remaining_quantity(
        doses_taken=160
    )

    assert refill_manager.is_supply_low(
        remaining_quantity=remaining_quantity,
        threshold=30
    ) is True

    request = refill_manager.request_refill()

    assert request["patient_id"] == patient.patient_id
    assert request["medication_id"] == medication.medication_id
    assert request["status"] == "requested"


def test_healthworker_can_process_refill_request(
    patient,
    healthworker,
    refill_manager
):
    healthworker.assign_patient(patient.patient_id)

    request = refill_manager.request_refill()

    assert request["patient_id"] in healthworker.assigned_patients

    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="in_progress"
    )

    updated_request = refill_manager.get_request(
        request["request_id"]
    )

    assert updated_request["status"] == "in_progress"


def test_healthworker_can_complete_refill_request(
    patient,
    healthworker,
    refill_manager
):
    healthworker.assign_patient(patient.patient_id)

    request = refill_manager.request_refill()

    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="in_progress"
    )

    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="completed"
    )

    completed_request = refill_manager.get_request(
        request["request_id"]
    )

    assert completed_request["status"] == "completed"
    assert completed_request["patient_id"] == patient.patient_id


def test_duplicate_active_refill_request_is_rejected(
    refill_manager
):
    refill_manager.request_refill()

    with pytest.raises(ValueError):
        refill_manager.request_refill()


def test_complete_refill_flow(
    patient,
    doctor,
    healthworker,
    treatment,
    medication,
    refill_manager
):
    # Doctor's prescription is connected to the patient's treatment.
    assert treatment.patient_id == patient.patient_id
    assert treatment.status == "active"

    assert medication.treatment_id == treatment.treatment_id
    assert medication.quantity == 180
    assert medication.frequency == 1

    # Healthworker is assigned to the patient.
    healthworker.assign_patient(patient.patient_id)

    assert patient.patient_id in healthworker.assigned_patients

    # The system calculates the patient's remaining supply.
    doses_taken = 160

    remaining_quantity = (
        refill_manager.calculate_remaining_quantity(
            doses_taken=doses_taken
        )
    )

    assert remaining_quantity == 20

    # The system detects that the supply is low.
    assert refill_manager.is_supply_low(
        remaining_quantity=remaining_quantity,
        threshold=30
    ) is True

    # The system creates an alert.
    alert = refill_manager.create_alert(
        remaining_quantity=remaining_quantity,
        threshold=30
    )

    assert alert["patient_id"] == patient.patient_id
    assert alert["medication_id"] == medication.medication_id
    assert alert["remaining_quantity"] == 20
    assert alert["status"] == "active"

    # Patient requests a refill.
    request = refill_manager.request_refill()

    assert request["patient_id"] == patient.patient_id
    assert request["medication_id"] == medication.medication_id
    assert request["status"] == "requested"

    # Healthworker begins processing the request.
    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="in_progress"
    )

    in_progress_request = refill_manager.get_request(
        request["request_id"]
    )

    assert in_progress_request["status"] == "in_progress"

    # Refill process is completed.
    refill_manager.update_request_status(
        request_id=request["request_id"],
        status="completed"
    )

    completed_request = refill_manager.get_request(
        request["request_id"]
    )

    assert completed_request["status"] == "completed"