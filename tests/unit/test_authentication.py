import pytest

from app.authentication import AuthenticationService


@pytest.fixture
def users():
    return [
        {
            "id": 1,
            "username": "doctor1",
            "password": "doctor123",
            "role": "doctor"
        },
        {
            "id": 2,
            "username": "patient1",
            "password": "patient123",
            "role": "patient"
        },
        {
            "id": 3,
            "username": "healthworker1",
            "password": "health123",
            "role": "healthworker"
        }
    ]


@pytest.fixture
def auth_service(users):
    return AuthenticationService(users)


def test_valid_login(auth_service):
    user = auth_service.login("doctor1", "doctor123")

    assert user is not None
    assert user["username"] == "doctor1"
    assert user["role"] == "doctor"


def test_login_with_wrong_password(auth_service):
    user = auth_service.login("doctor1", "wrongpassword")

    assert user is None
    assert auth_service.current_user is None


def test_login_with_unknown_username(auth_service):
    user = auth_service.login("unknown_user", "password123")

    assert user is None
    assert auth_service.current_user is None


def test_login_with_empty_username(auth_service):
    user = auth_service.login("", "doctor123")

    assert user is None
    assert auth_service.current_user is None


def test_login_with_empty_password(auth_service):
    user = auth_service.login("doctor1", "")

    assert user is None
    assert auth_service.current_user is None


def test_logout(auth_service):
    auth_service.login("doctor1", "doctor123")

    assert auth_service.current_user is not None

    auth_service.logout()

    assert auth_service.current_user is None

def test_patient_can_login(auth_service):
    user = auth_service.login("patient1", "patient123")

    assert user is not None
    assert user["username"] == "patient1"
    assert user["role"] == "patient"


def test_healthworker_can_login(auth_service):
    user = auth_service.login("healthworker1", "health123")

    assert user is not None
    assert user["username"] == "healthworker1"
    assert user["role"] == "healthworker"


def test_logout_when_not_logged_in(auth_service):
    auth_service.logout()

    assert auth_service.current_user is None