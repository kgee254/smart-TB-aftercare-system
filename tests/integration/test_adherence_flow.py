import pytest
from datetime import date

from app.patient import Patient
from app.doctor import Doctor
from app.healthworker import HealthWorker
from app.treatment import Treatment
from app.medication import Medication
from app.adherence import AdherenceTracker


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
def adherence_tracker(patient, medication):
    return AdherenceTracker(
        patient_id=patient.patient_id,
        medication_id=medication.medication_id
    )


def test_adherence_belongs_to_correct_patient_and_medication(
    patient,
    medication,
    adherence_tracker
):
    assert adherence_tracker.patient_id == patient.patient_id
    assert adherence_tracker.medication_id == medication.medication_id


def test_patient_can_record_medication_adherence(
    patient,
    medication,
    adherence_tracker
):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="taken"
    )

    history = adherence_tracker.get_history()

    assert len(history) == 1
    assert history[0]["patient_id"] == patient.patient_id
    assert history[0]["medication_id"] == medication.medication_id
    assert history[0]["status"] == "taken"


def test_patient_can_record_multiple_taken_and_missed_doses(
    adherence_tracker
):
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

    history = adherence_tracker.get_history()

    assert len(history) == 4
    assert history[2]["status"] == "missed"


def test_patient_adherence_percentage_is_calculated(
    patient,
    medication,
    adherence_tracker
):
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

    adherence_percentage = (
        adherence_tracker.get_adherence_percentage()
    )

    assert adherence_percentage == 75.0


def test_low_adherence_can_be_identified(adherence_tracker):
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

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 13),
        status="missed"
    )

    assert adherence_tracker.get_adherence_percentage() == 25.0


def test_healthworker_can_monitor_patient_adherence(
    patient,
    medication,
    adherence_tracker,
    healthworker
):
    healthworker.assign_patient(patient.patient_id)

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

    patient_adherence = {
        "patient_id": patient.patient_id,
        "medication_id": medication.medication_id,
        "adherence_rate": (
            adherence_tracker.get_adherence_percentage()
        )
    }

    assert patient_adherence["patient_id"] == patient.patient_id
    assert patient_adherence["adherence_rate"] == pytest.approx(33.33, abs=0.01)


def test_doctor_can_monitor_patient_adherence(
    patient,
    medication,
    adherence_tracker,
    doctor
):
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

    adherence_rate = adherence_tracker.get_adherence_percentage()

    assert patient.patient_id == adherence_tracker.patient_id
    assert medication.medication_id == adherence_tracker.medication_id
    assert adherence_rate == pytest.approx(66.67, abs=0.01)


def test_complete_adherence_flow(
    patient,
    doctor,
    healthworker,
    treatment,
    medication,
    adherence_tracker
):
    # Healthworker is assigned to the patient
    healthworker.assign_patient(patient.patient_id)

    # Treatment belongs to the patient
    assert treatment.patient_id == patient.patient_id

    # Medication belongs to the treatment
    assert medication.treatment_id == treatment.treatment_id

    # Adherence belongs to the patient and medication
    assert adherence_tracker.patient_id == patient.patient_id
    assert adherence_tracker.medication_id == medication.medication_id

    # Patient records doses
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

    # System calculates adherence
    adherence_rate = adherence_tracker.get_adherence_percentage()

    assert adherence_rate == pytest.approx(66.67, abs=0.01)

    # Patient remains connected to the treatment
    assert treatment.patient_id == patient.patient_id

    # Medication remains connected to the treatment
    assert medication.treatment_id == treatment.treatment_id

    # Adherence remains connected to the medication
    assert adherence_tracker.medication_id == medication.medication_id