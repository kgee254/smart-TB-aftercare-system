from datetime import date

from app.patient import Patient
from app.treatment import Treatment
from app.medication import Medication


def _display_doctor_menu():
    """Display the doctor menu options."""
    print("\n" + "=" * 50)
    print("   DOCTOR MENU")
    print("=" * 50)
    print("1. View all patients")
    print("2. View a patient's details")
    print("3. Create treatment for a patient")
    print("4. Prescribe medication")
    print("5. View patient treatments")
    print("6. View patient adherence")
    print("7. View patient symptoms")
    print("8. Record clinical note")
    print("9. Complete a treatment")
    print("10. Update treatment instructions")
    print("11. Logout")
    print("=" * 50)


def _view_all_patients(user, data_manager, services):
    """Display a list of all registered patients."""
    patients = data_manager.load_data("patients.json") or []

    if not patients:
        print("\nNo patients registered in the system.")
        return

    print(f"\n--- All Patients ({len(patients)}) ---")
    for p in patients:
        attention = " ⚠ NEEDS ATTENTION" if p.get("needs_attention") else ""
        print(f"  ID: {p.get('patient_id')}  "
              f"Name: {p.get('name')}  "
              f"Phone: {p.get('phone')}{attention}")


def _view_patient_details(user, data_manager, services):
    """View detailed information for a specific patient."""
    patients = data_manager.load_data("patients.json") or []

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    patient = None
    for p in patients:
        if p.get("patient_id") == patient_id:
            patient = p
            break

    if patient is None:
        print(f"Patient with ID {patient_id} not found.")
        return

    print(f"\n--- Patient Details ---")
    print(f"  Patient ID  : {patient.get('patient_id')}")
    print(f"  Name        : {patient.get('name')}")
    print(f"  Username    : {patient.get('username')}")
    print(f"  Phone       : {patient.get('phone')}")
    print(f"  Attention   : {'Yes' if patient.get('needs_attention') else 'No'}")

    # Also show their treatments
    treatments = services["treatment"].get_patient_treatments(patient_id)
    if treatments:
        print(f"  Treatments  : {len(treatments)}")
        for t in treatments:
            print(f"    - T{t.get('treatment_id')}: "
                  f"{t.get('status')} "
                  f"(started {t.get('start_date')})")


def _create_treatment(user, data_manager, services):
    """Create a new treatment for a patient."""
    treatment_service = services["treatment"]

    print("\n--- Create Treatment ---")

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    # Verify patient exists
    patients = data_manager.load_data("patients.json") or []
    if not any(p.get("patient_id") == patient_id for p in patients):
        print(f"Patient with ID {patient_id} not found.")
        return

    start_date = date.today().isoformat()

    duration_input = input("Treatment duration (days, e.g. 180): ").strip()
    try:
        duration_days = int(duration_input)
    except ValueError:
        print("Invalid duration.")
        return

    instructions = input("Treatment instructions: ").strip()

    # Generate next treatment ID
    all_treatments = treatment_service.get_all_treatments()
    if all_treatments:
        next_id = max(t.get("treatment_id", 0) for t in all_treatments) + 1
    else:
        next_id = 1

    try:
        treatment = treatment_service.create_treatment(
            patient_id=patient_id,
            start_date=start_date,
            duration_days=duration_days,
            instructions=instructions,
            treatment_id=next_id
        )
        print(f"\nTreatment created successfully!")
        print(f"  Treatment ID : {treatment.treatment_id}")
        print(f"  Patient ID   : {patient_id}")
        print(f"  Duration     : {duration_days} days")
        print(f"  Status       : {treatment.status}")
    except ValueError as e:
        print(f"\nError: {e}")


def _prescribe_medication(user, data_manager, services):
    """Prescribe a medication for an existing treatment."""
    print("\n--- Prescribe Medication ---")

    treatment_id_input = input("Enter treatment ID: ").strip()
    try:
        treatment_id = int(treatment_id_input)
    except ValueError:
        print("Invalid treatment ID.")
        return

    # Verify treatment exists
    treatment = services["treatment"].get_treatment(treatment_id)
    if treatment is None:
        print(f"Treatment with ID {treatment_id} not found.")
        return

    name = input("Medication name (e.g. Rifampicin): ").strip()
    if not name:
        print("Medication name cannot be empty.")
        return

    dosage_input = input("Dosage in mg (e.g. 600): ").strip()
    try:
        dosage = int(dosage_input)
    except ValueError:
        print("Invalid dosage.")
        return

    frequency_input = input("Frequency per day (e.g. 1): ").strip()
    try:
        frequency = int(frequency_input)
    except ValueError:
        print("Invalid frequency.")
        return

    quantity_input = input("Total quantity/tablets (e.g. 180): ").strip()
    try:
        quantity = int(quantity_input)
    except ValueError:
        print("Invalid quantity.")
        return

    duration_input = input("Duration in days (e.g. 180): ").strip()
    try:
        duration_days = int(duration_input)
    except ValueError:
        print("Invalid duration.")
        return

    instructions = input("Instructions (e.g. Take once daily): ").strip()

    # Generate next medication ID
    medications = data_manager.load_data("medications.json") or []
    if medications:
        next_id = max(m.get("medication_id", 0) for m in medications) + 1
    else:
        next_id = 1

    # Create the Medication domain object (for validation)
    try:
        medication = Medication(
            medication_id=next_id,
            treatment_id=treatment_id,
            name=name,
            dosage=dosage,
            frequency=frequency,
            quantity=quantity,
            duration_days=duration_days,
            instructions=instructions
        )
    except ValueError as e:
        print(f"\nError creating medication: {e}")
        return

    # Save to JSON
    med_dict = medication.get_details()
    medications.append(med_dict)
    data_manager.save_data("medications.json", medications)

    print(f"\nMedication prescribed successfully!")
    print(f"  Medication ID : {medication.medication_id}")
    print(f"  Name         : {medication.name}")
    print(f"  Dosage       : {medication.dosage} mg")
    print(f"  Frequency    : {medication.frequency}x daily")
    print(f"  Quantity     : {medication.quantity}")


def _view_patient_treatments(user, data_manager, services):
    """View all treatments for a specific patient."""
    treatment_service = services["treatment"]

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    treatments = treatment_service.get_patient_treatments(patient_id)

    if not treatments:
        print(f"\nNo treatments found for patient {patient_id}.")
        return

    print(f"\n--- Treatments for Patient {patient_id} ---")
    for t in treatments:
        print(f"  Treatment ID : {t.get('treatment_id')}")
        print(f"  Start Date   : {t.get('start_date')}")
        print(f"  Duration     : {t.get('duration_days')} days")
        print(f"  Status       : {t.get('status')}")
        print(f"  Instructions : {t.get('instructions')}")
        print("  " + "-" * 35)


def _view_patient_adherence(user, data_manager, services):
    """View adherence data for a specific patient."""
    adherence_service = services["adherence"]

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    overall_pct = adherence_service.calculate_adherence(patient_id)
    missed = adherence_service.count_missed_doses(patient_id)

    print(f"\n--- Adherence for Patient {patient_id} ---")
    print(f"  Overall adherence : {overall_pct}%")
    print(f"  Total missed     : {missed} doses")

    # Per-medication breakdown
    medications = data_manager.load_data("medications.json") or []
    treatments = services["treatment"].get_patient_treatments(patient_id)

    patient_meds = []
    for t in treatments:
        patient_meds.extend([
            m for m in medications
            if m.get("treatment_id") == t.get("treatment_id")
        ])

    for m in patient_meds:
        med_id = m.get("medication_id")
        med_pct = adherence_service.calculate_adherence(
            patient_id, medication_id=med_id
        )
        med_missed = adherence_service.count_missed_doses(
            patient_id, medication_id=med_id
        )
        print(f"  {m.get('name')} (ID {med_id}): "
              f"{med_pct}% adherence, "
              f"{med_missed} missed")


def _view_patient_symptoms(user, data_manager, services):
    """View symptom history for a specific patient."""
    symptom_service = services["symptom"]

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    history = symptom_service.get_patient_history(patient_id)

    if not history:
        print(f"\nNo symptom records for patient {patient_id}.")
        return

    print(f"\n--- Symptom History for Patient {patient_id} ---")
    for record in history:
        print(f"  Date       : {record.get('date')}")
        print(f"  Symptoms   : {', '.join(record.get('symptoms', []))}")
        if record.get('other_symptom'):
            print(f"  Other      : {record.get('other_symptom')}")
        if record.get('severity'):
            print(f"  Severity   : {record.get('severity')}")
        if record.get('notes'):
            print(f"  Notes      : {record.get('notes')}")
        print("  " + "-" * 35)


def _record_clinical_note(user, data_manager, services):
    """Record a clinical note for a patient."""
    print("\n--- Record Clinical Note ---")

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    # Verify patient exists
    patients = data_manager.load_data("patients.json") or []
    if not any(p.get("patient_id") == patient_id for p in patients):
        print(f"Patient with ID {patient_id} not found.")
        return

    note = input("Enter clinical note: ").strip()
    if not note:
        print("Note cannot be empty.")
        return

    doctor_id = user.get("doctor_id")

    note_record = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "note": note,
        "date": date.today().isoformat()
    }

    # Save clinical notes to a separate file
    clinical_notes = data_manager.load_data("clinical_notes.json") or []
    clinical_notes.append(note_record)
    data_manager.save_data("clinical_notes.json", clinical_notes)

    print(f"\nClinical note recorded for patient {patient_id}.")


def _complete_treatment(user, data_manager, services):
    """Mark a treatment as completed."""
    treatment_service = services["treatment"]

    print("\n--- Complete Treatment ---")

    treatment_id_input = input("Enter treatment ID to complete: ").strip()
    try:
        treatment_id = int(treatment_id_input)
    except ValueError:
        print("Invalid treatment ID.")
        return

    # Confirm
    treatment = treatment_service.get_treatment(treatment_id)
    if treatment is None:
        print(f"Treatment with ID {treatment_id} not found.")
        return

    if treatment.get("status") == "completed":
        print("This treatment is already completed.")
        return

    confirm = input(
        f"Confirm completing treatment {treatment_id}? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Cancelled.")
        return

    try:
        updated = treatment_service.complete_treatment(treatment_id)
        print(f"\nTreatment {treatment_id} marked as completed.")
    except ValueError as e:
        print(f"\nError: {e}")


def _update_treatment_instructions(user, data_manager, services):
    """Update the instructions on an existing treatment."""
    treatment_service = services["treatment"]

    print("\n--- Update Treatment Instructions ---")

    treatment_id_input = input("Enter treatment ID: ").strip()
    try:
        treatment_id = int(treatment_id_input)
    except ValueError:
        print("Invalid treatment ID.")
        return

    treatment = treatment_service.get_treatment(treatment_id)
    if treatment is None:
        print(f"Treatment with ID {treatment_id} not found.")
        return

    print(f"Current instructions: {treatment.get('instructions')}")
    new_instructions = input("Enter new instructions: ").strip()
    if not new_instructions:
        print("Instructions cannot be empty.")
        return

    try:
        updated = treatment_service.update_treatment(
            treatment_id, instructions=new_instructions
        )
        print(f"\nTreatment {treatment_id} instructions updated.")
    except ValueError as e:
        print(f"\nError: {e}")


def doctor_menu(user, data_manager, services):
    """
    Run the doctor menu loop.

    Parameters:
        user (dict): The logged-in doctor user dict.
        data_manager (DataManager): For JSON persistence.
        services (dict): Dict of service instances.
    """
    while True:
        _display_doctor_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            _view_all_patients(user, data_manager, services)
        elif choice == "2":
            _view_patient_details(user, data_manager, services)
        elif choice == "3":
            _create_treatment(user, data_manager, services)
        elif choice == "4":
            _prescribe_medication(user, data_manager, services)
        elif choice == "5":
            _view_patient_treatments(user, data_manager, services)
        elif choice == "6":
            _view_patient_adherence(user, data_manager, services)
        elif choice == "7":
            _view_patient_symptoms(user, data_manager, services)
        elif choice == "8":
            _record_clinical_note(user, data_manager, services)
        elif choice == "9":
            _complete_treatment(user, data_manager, services)
        elif choice == "10":
            _update_treatment_instructions(user, data_manager, services)
        elif choice == "11":
            print(f"\nLogged out. Goodbye, {user.get('name', 'Doctor')}!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 11.")
