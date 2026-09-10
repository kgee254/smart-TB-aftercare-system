import pytest

from app.healthworker import HealthWorker


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
def patients():
    return [
        {
            "patient_id": 1,
            "name": "John Kamau",
            "treatment_status": "active",
            "adherence_rate": 95,
            "needs_attention": False
        },
        {
            "patient_id": 2,
            "name": "Mary Njeri",
            "treatment_status": "active",
            "adherence_rate": 65,
            "needs_attention": True
        },
        {
            "patient_id": 3,
            "name": "Peter Mwangi",
            "treatment_status": "completed",
            "adherence_rate": 100,
            "needs_attention": False
        }
    ]


def test_create_healthworker(healthworker):
    assert healthworker.healthworker_id == 1
    assert healthworker.name == "Grace Wambui"
    assert healthworker.username == "healthworker1"
    assert healthworker.phone == "0733333333"


def test_healthworker_role_is_healthworker(healthworker):
    assert healthworker.role == "healthworker"


def test_healthworker_can_view_profile(healthworker):
    profile = healthworker.get_profile()

    assert profile["healthworker_id"] == 1
    assert profile["name"] == "Grace Wambui"
    assert profile["username"] == "healthworker1"
    assert profile["phone"] == "0733333333"


def test_healthworker_profile_does_not_expose_password(healthworker):
    profile = healthworker.get_profile()

    assert "password" not in profile


def test_healthworker_can_view_assigned_patients(healthworker, patients):
    healthworker.assign_patient(1)
    healthworker.assign_patient(2)

    assigned_patients = healthworker.view_assigned_patients(patients)

    assert len(assigned_patients) == 2
    assert assigned_patients[0]["patient_id"] == 1
    assert assigned_patients[1]["patient_id"] == 2


def test_healthworker_can_view_assigned_patient(healthworker, patients):
    healthworker.assign_patient(1)

    patient = healthworker.view_patient(1, patients)

    assert patient is not None
    assert patient["patient_id"] == 1
    assert patient["name"] == "John Kamau"


def test_healthworker_can_identify_patient_needing_attention(
    healthworker,
    patients
):
    healthworker.assign_patient(1)
    healthworker.assign_patient(2)

    patients_needing_attention = healthworker.get_patients_needing_attention(
        patients
    )

    assert len(patients_needing_attention) == 1
    assert patients_needing_attention[0]["patient_id"] == 2


def test_healthworker_can_record_followup(healthworker):
    followup = healthworker.record_followup(
        patient_id=2,
        action="Called patient to discuss missed medication doses."
    )

    assert followup["healthworker_id"] == 1
    assert followup["patient_id"] == 2
    assert followup["action"] == (
        "Called patient to discuss missed medication doses."
    )


def test_healthworker_cannot_have_empty_name():
    with pytest.raises(ValueError):
        HealthWorker(
            healthworker_id=1,
            name="",
            username="healthworker1",
            password="health123",
            phone="0733333333"
        )