import pytest

from app.doctor import Doctor


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
def patients():
    return [
        {
            "patient_id": 1,
            "name": "John Kamau",
            "username": "john1",
            "phone": "0711111111"
        },
        {
            "patient_id": 2,
            "name": "Mary Njeri",
            "username": "mary1",
            "phone": "0722222222"
        }
    ]


def test_create_doctor(doctor):
    assert doctor.doctor_id == 1
    assert doctor.name == "Dr. Jane Wanjiku"
    assert doctor.username == "doctor1"
    assert doctor.phone == "0712345678"
    assert doctor.specialization == "TB Specialist"


def test_doctor_role_is_doctor(doctor):
    assert doctor.role == "doctor"


def test_doctor_can_view_profile(doctor):
    profile = doctor.get_profile()

    assert profile["doctor_id"] == 1
    assert profile["name"] == "Dr. Jane Wanjiku"
    assert profile["username"] == "doctor1"
    assert profile["phone"] == "0712345678"
    assert profile["specialization"] == "TB Specialist"


def test_doctor_profile_does_not_expose_password(doctor):
    profile = doctor.get_profile()

    assert "password" not in profile


def test_doctor_can_view_patient(doctor, patients):
    patient = doctor.view_patient(1, patients)

    assert patient is not None
    assert patient["patient_id"] == 1
    assert patient["name"] == "John Kamau"


def test_doctor_cannot_view_nonexistent_patient(doctor, patients):
    patient = doctor.view_patient(999, patients)

    assert patient is None


def test_doctor_can_record_clinical_note(doctor):
    note = doctor.record_clinical_note(
        patient_id=1,
        note="Patient reports improvement in symptoms."
    )

    assert note["patient_id"] == 1
    assert note["doctor_id"] == 1
    assert note["note"] == "Patient reports improvement in symptoms."


def test_doctor_cannot_have_empty_name():
    with pytest.raises(ValueError):
        Doctor(
            doctor_id=1,
            name="",
            username="doctor1",
            password="doctor123",
            phone="0712345678",
            specialization="TB Specialist"
        )