from datetime import date

from app.authentication import AuthenticationService
from app.patient import Patient
from app.doctor import Doctor
from app.healthworker import HealthWorker
from cli.patient_menu import patient_menu
from cli.doctor_menu import doctor_menu
from cli.healthworker_menu import healthworker_menu


def _load_users(data_manager):
    """
    Load all user accounts from patients.json, doctors.json,
    and healthworkers.json and merge them into a single list
    compatible with AuthenticationService.
    """
    patients = data_manager.load_data("patients.json") or []
    doctors = data_manager.load_data("doctors.json") or []
    healthworkers = data_manager.load_data("healthworkers.json") or []

    users = []
    users.extend(patients)
    users.extend(doctors)
    users.extend(healthworkers)

    return users


def _display_main_menu():
    """Display the main menu options."""
    print("\n" + "=" * 50)
    print("   SMART TB AFTERCARE SYSTEM")
    print("=" * 50)
    print("1. Login")
    print("2. Register")
    print("3. Exit")
    print("=" * 50)


def _get_choice():
    """Prompt the user for a menu choice."""
    choice = input("Enter your choice: ").strip()
    return choice


def _login(data_manager, services):
    """
    Handle user login.

    Loads all users from JSON, authenticates via
    AuthenticationService, and routes to the correct
    role-specific menu.
    """
    users = _load_users(data_manager)
    auth_service = AuthenticationService(users)

    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    user = auth_service.login(username, password)

    if user is None:
        print("\nLogin failed. Invalid username or password.")
        return

    role = user.get("role", "")
    print(f"\nWelcome, {user.get('name', username)}!")

    if role == "patient":
        patient_menu(user, data_manager, services)
    elif role == "doctor":
        doctor_menu(user, data_manager, services)
    elif role == "healthworker":
        healthworker_menu(user, data_manager, services)
    else:
        print(f"Unknown role: {role}")


def _register(data_manager):
    """
    Handle new patient registration.

    Creates a Patient object, appends it to patients.json,
    and saves the updated list.
    """
    print("\n--- Patient Registration ---")

    patients = data_manager.load_data("patients.json") or []

    # Generate next patient ID
    if patients:
        next_id = max(p["patient_id"] for p in patients) + 1
    else:
        next_id = 1

    name = input("Full name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    username = input("Choose a username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    # Check for duplicate username
    all_users = _load_users(data_manager)
    for u in all_users:
        if u.get("username") == username:
            print("That username is already taken.")
            return

    password = input("Choose a password: ").strip()
    if not password:
        print("Password cannot be empty.")
        return

    phone = input("Phone number: ").strip()

    patient = Patient(
        patient_id=next_id,
        name=name,
        username=username,
        password=password,
        phone=phone
    )

    # Convert to dict for JSON storage
    patient_dict = {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "username": patient.username,
        "password": patient.password,
        "phone": patient.phone,
        "role": patient.role,
        "needs_attention": False
    }

    patients.append(patient_dict)
    data_manager.save_data("patients.json", patients)

    print(f"\nRegistration successful! Your patient ID is {next_id}.")
    print("You can now login from the main menu.")


def main_menu(data_manager, services):
    """
    Run the main menu loop.

    This is the entry point for the interactive CLI.
    """
    while True:
        _display_main_menu()
        choice = _get_choice()

        if choice == "1":
            _login(data_manager, services)
        elif choice == "2":
            _register(data_manager)
        elif choice == "3":
            print("\nThank you for using the Smart TB Aftercare System.")
            print("Stay healthy! Goodbye.\n")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
