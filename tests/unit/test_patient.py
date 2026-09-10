import pytest

from app.patient import Patient


@pytest.fixture
def patient():
    return Patient(
        patient_id=1,
        name="John Kamau",
        username="john1",
        password="john123",
        phone="0712345678"
    )


def test_create_patient(patient):
    assert patient.patient_id == 1
    assert patient.name == "John Kamau"
    assert patient.username == "john1"
    assert patient.phone == "0712345678"


def test_patient_role_is_patient(patient):
    assert patient.role == "patient"


def test_patient_can_view_profile(patient):
    profile = patient.get_profile()

    assert profile["patient_id"] == 1
    assert profile["name"] == "John Kamau"
    assert profile["username"] == "john1"
    assert profile["phone"] == "0712345678"


def test_patient_profile_does_not_expose_password(patient):
    profile = patient.get_profile()

    assert "password" not in profile


def test_patient_can_update_phone_number(patient):
    patient.update_phone("0798765432")

    assert patient.phone == "0798765432"


def test_patient_cannot_have_empty_name():
    with pytest.raises(ValueError):
        Patient(
            patient_id=1,
            name="",
            username="john1",
            password="john123",
            phone="0712345678"
        )


def test_patient_cannot_have_empty_username():
    with pytest.raises(ValueError):
        Patient(
            patient_id=1,
            name="John Kamau",
            username="",
            password="john123",
            phone="0712345678"
        )