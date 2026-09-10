import pytest
from datetime import date

from app.patient import Patient
from app.doctor import Doctor
from app.healthworker import HealthWorker
from app.treatment import Treatment
from app.medication import Medication
from app.adherence import AdherenceTracker
from app.symptoms import SymptomTracker
from app.followup import FollowUpTracker


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


@pytest.fixture
def symptom_tracker(patient):
    return SymptomTracker(
        patient_id=patient.patient_id
    )


@pytest.fixture
def followup_tracker(healthworker):
    return FollowUpTracker(
        healthworker_id=healthworker.healthworker_id
    )


def test_healthworker_can_identify_patient_with_low_adherence(
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

    adherence_rate = adherence_tracker.get_adherence_percentage()

    assert adherence_rate == pytest.approx(33.33, abs=0.01)
    assert patient.patient_id in healthworker.assigned_patient_ids


def test_patient_symptoms_can_trigger_followup(
    patient,
    symptom_tracker,
    followup_tracker
):
    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 13),
        symptoms=["cough", "fever"],
        severity="severe",
        notes="Patient reports worsening symptoms."
    )

    symptom_history = symptom_tracker.get_history()

    assert len(symptom_history) == 1
    assert symptom_history[0]["symptoms"] == [
        "cough",
        "fever"
    ]
    assert symptom_history[0]["severity"] == "severe"

    case = followup_tracker.create_case(
        patient_id=patient.patient_id,
        reason="Patient reported severe symptoms."
    )

    assert case["patient_id"] == patient.patient_id
    assert case["status"] == "open"


def test_low_adherence_can_create_followup_case(
    patient,
    medication,
    adherence_tracker,
    followup_tracker
):
    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 10),
        status="missed"
    )

    adherence_tracker.record_dose(
        dose_date=date(2026, 9, 11),
        status="missed"
    )

    adherence_rate = adherence_tracker.get_adherence_percentage()

    assert adherence_rate == 0.0

    case = followup_tracker.create_case(
        patient_id=patient.patient_id,
        reason="Patient has missed medication doses."
    )

    assert case["patient_id"] == patient.patient_id
    assert case["reason"] == (
        "Patient has missed medication doses."
    )
    assert case["status"] == "open"


def test_healthworker_can_follow_up_on_patient_problem(
    patient,
    healthworker,
    followup_tracker
):
    healthworker.assign_patient(patient.patient_id)

    case = followup_tracker.create_case(
        patient_id=patient.patient_id,
        reason="Patient reported worsening symptoms."
    )

    followup_tracker.update_status(
        case_id=case["case_id"],
        status="in_progress"
    )

    followup_tracker.update_case(
        case_id=case["case_id"],
        action="Called patient to assess reported symptoms."
    )

    updated_case = followup_tracker.get_case(
        case["case_id"]
    )

    assert updated_case["status"] == "in_progress"
    assert updated_case["action"] == (
        "Called patient to assess reported symptoms."
    )


def test_healthworker_can_escalate_patient_to_doctor(
    patient,
    doctor,
    healthworker,
    symptom_tracker,
    followup_tracker
):
    healthworker.assign_patient(patient.patient_id)

    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 13),
        symptoms=["cough", "fever"],
        severity="severe",
        notes="Symptoms are getting worse."
    )

    case = followup_tracker.create_case(
        patient_id=patient.patient_id,
        reason="Worsening symptoms require clinical review."
    )

    followup_tracker.update_status(
        case_id=case["case_id"],
        status="in_progress"
    )

    followup_tracker.escalate_case(
        case_id=case["case_id"],
        reason="Patient requires doctor review."
    )

    escalated_case = followup_tracker.get_case(
        case["case_id"]
    )

    assert escalated_case["patient_id"] == patient.patient_id
    assert escalated_case["healthworker_id"] == healthworker.healthworker_id
    assert escalated_case["status"] == "escalated"
    assert escalated_case["escalation_reason"] == (
        "Patient requires doctor review."
    )

    assert doctor.doctor_id == 1


def test_complete_escalation_flow(
    patient,
    doctor,
    healthworker,
    treatment,
    medication,
    adherence_tracker,
    symptom_tracker,
    followup_tracker
):
    # 1. Healthworker is assigned to the patient
    healthworker.assign_patient(patient.patient_id)

    # 2. Patient has an active treatment
    assert treatment.patient_id == patient.patient_id
    assert treatment.status == "active"

    # 3. Medication belongs to the patient's treatment
    assert medication.treatment_id == treatment.treatment_id

    # 4. Patient misses several medication doses
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

    # 5. Patient reports worsening symptoms
    symptom_tracker.record_checkin(
        checkin_date=date(2026, 9, 13),
        symptoms=["cough", "fever"],
        severity="severe",
        notes="Patient reports worsening symptoms."
    )

    # 6. System has evidence that the patient needs attention
    adherence_rate = adherence_tracker.get_adherence_percentage()

    assert adherence_rate == pytest.approx(33.33, abs=0.01)

    symptom_history = symptom_tracker.get_history()

    assert symptom_history[0]["severity"] == "severe"

    # 7. Healthworker creates a follow-up case
    case = followup_tracker.create_case(
        patient_id=patient.patient_id,
        reason=(
            "Low adherence and worsening symptoms."
        )
    )

    assert case["patient_id"] == patient.patient_id
    assert case["status"] == "open"

    # 8. Healthworker starts follow-up
    followup_tracker.update_status(
        case_id=case["case_id"],
        status="in_progress"
    )

    followup_tracker.update_case(
        case_id=case["case_id"],
        action="Contacted patient and reviewed symptoms."
    )

    # 9. Healthworker escalates the case
    followup_tracker.escalate_case(
        case_id=case["case_id"],
        reason="Patient requires doctor review."
    )

    # 10. Verify final case state
    final_case = followup_tracker.get_case(
        case["case_id"]
    )

    assert final_case["patient_id"] == patient.patient_id
    assert final_case["healthworker_id"] == healthworker.healthworker_id
    assert final_case["status"] == "escalated"
    assert final_case["action"] == (
        "Contacted patient and reviewed symptoms."
    )
    assert final_case["escalation_reason"] == (
        "Patient requires doctor review."
    )

    # 11. Doctor remains the clinical decision-maker
    assert doctor.doctor_id == 1