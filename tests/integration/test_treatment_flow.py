import pytest
from datetime import date

from app.patient import Patient
from app.doctor import Doctor
from app.treatment import Treatment
from app.medication import Medication


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


def test_doctor_can_create_treatment_for_patient(patient, doctor):
    treatment = Treatment(
        treatment_id=101,
        patient_id=patient.patient_id,
        start_date=date(2026, 9, 10),
        duration_days=180,
        instructions="Take medication according to the prescription."
    )

    assert treatment.patient_id == patient.patient_id
    assert treatment.patient_id == 1


def test_treatment_is_active_when_created(patient, doctor):
    treatment = Treatment(
        treatment_id=101,
        patient_id=patient.patient_id,
        start_date=date(2026, 9, 10),
        duration_days=180,
        instructions="Take medication according to the prescription."
    )

    assert treatment.status == "active"


def test_medication_can_be_attached_to_treatment(
    patient,
    doctor,
    treatment
):
    medication = Medication(
        medication_id=201,
        treatment_id=treatment.treatment_id,
        name="Rifampicin",
        dosage=600,
        frequency=1,
        quantity=180,
        duration_days=180,
        instructions="Take once daily."
    )

    assert medication.treatment_id == treatment.treatment_id
    assert medication.treatment_id == 101


def test_complete_treatment_relationship(
    patient,
    doctor,
    treatment,
    medication
):
    assert patient.patient_id == treatment.patient_id
    assert treatment.treatment_id == medication.treatment_id


def test_treatment_and_medication_belong_to_correct_patient(
    patient,
    treatment,
    medication
):
    assert treatment.patient_id == patient.patient_id
    assert medication.treatment_id == treatment.treatment_id


def test_doctor_can_create_treatment_and_prescription(
    patient,
    doctor
):
    treatment = Treatment(
        treatment_id=101,
        patient_id=patient.patient_id,
        start_date=date(2026, 9, 10),
        duration_days=180,
        instructions="Take medication according to the prescription."
    )

    medication = Medication(
        medication_id=201,
        treatment_id=treatment.treatment_id,
        name="Rifampicin",
        dosage=600,
        frequency=1,
        quantity=180,
        duration_days=180,
        instructions="Take once daily."
    )

    assert treatment.patient_id == patient.patient_id
    assert treatment.status == "active"

    assert medication.treatment_id == treatment.treatment_id
    assert medication.name == "Rifampicin"
    assert medication.dosage == 600
    assert medication.frequency == 1
    assert medication.quantity == 180


def test_treatment_can_be_completed_after_medication_is_prescribed(
    treatment,
    medication
):
    treatment.update_status("completed")

    assert treatment.status == "completed"
    assert medication.treatment_id == treatment.treatment_id