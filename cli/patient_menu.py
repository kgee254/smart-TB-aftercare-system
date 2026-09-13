from datetime import date


def _display_patient_menu():
    """Display the patient menu options."""
    print("\n" + "=" * 50)
    print("   PATIENT MENU")
    print("=" * 50)
    print("1. View my treatment")
    print("2. View my medications")
    print("3. Record dose (taken/missed)")
    print("4. View my adherence")
    print("5. Symptom check-in")
    print("6. View my symptom history")
    print("7. Request medication refill")
    print("8. View refill status")
    print("9. Logout")
    print("=" * 50)


def _view_treatment(user, data_manager, services):
    """Display all active treatments for the logged-in patient."""
    patient_id = user["patient_id"]
    treatment_service = services["treatment"]

    treatments = treatment_service.get_patient_treatments(patient_id)

    if not treatments:
        print("\nYou have no treatments on record.")
        return

    print(f"\n--- Your Treatments ---")
    for t in treatments:
        print(f"  Treatment ID : {t.get('treatment_id')}")
        print(f"  Start Date   : {t.get('start_date')}")
        print(f"  Duration     : {t.get('duration_days')} days")
        print(f"  Status       : {t.get('status')}")
        print(f"  Instructions : {t.get('instructions')}")
        print("  " + "-" * 35)


def _view_medications(user, data_manager, services):
    """Display all medications belonging to the patient's treatments."""
    patient_id = user["patient_id"]
    treatment_service = services["treatment"]

    treatments = treatment_service.get_patient_treatments(patient_id)

    if not treatments:
        print("\nYou have no treatments, hence no medications.")
        return

    # Load medications and match by treatment_id
    medications = data_manager.load_data("medications.json") or []

    print(f"\n--- Your Medications ---")
    for t in treatments:
        treatment_meds = [
            m for m in medications
            if m.get("treatment_id") == t.get("treatment_id")
        ]
        for m in treatment_meds:
            print(f"  Medication ID : {m.get('medication_id')}")
            print(f"  Name          : {m.get('name')}")
            print(f"  Dosage        : {m.get('dosage')} mg")
            print(f"  Frequency     : {m.get('frequency')}x daily")
            print(f"  Remaining     : {m.get('quantity')} tablets")
            print(f"  Instructions  : {m.get('instructions')}")
            print("  " + "-" * 35)


def _record_dose(user, data_manager, services):
    """Record a taken or missed dose for today."""
    patient_id = user["patient_id"]
    adherence_service = services["adherence"]

    # Show available medications
    medications = data_manager.load_data("medications.json") or []
    treatments = services["treatment"].get_patient_treatments(patient_id)

    patient_meds = []
    for t in treatments:
        patient_meds.extend([
            m for m in medications
            if m.get("treatment_id") == t.get("treatment_id")
        ])

    if not patient_meds:
        print("\nYou have no medications to record a dose for.")
        return

    print("\n--- Record Dose ---")
    print("Your medications:")
    for m in patient_meds:
        print(f"  [{m.get('medication_id')}] {m.get('name')}")

    med_id_input = input("Enter medication ID: ").strip()
    try:
        med_id = int(med_id_input)
    except ValueError:
        print("Invalid medication ID.")
        return

    # Verify this medication belongs to the patient
    if not any(m.get("medication_id") == med_id for m in patient_meds):
        print("That medication does not belong to you.")
        return

    dose_date = date.today().isoformat()

    print("Was the dose taken or missed?")
    print("1. Taken")
    print("2. Missed")
    status_choice = input("Enter choice: ").strip()

    if status_choice == "1":
        status = "taken"
    elif status_choice == "2":
        status = "missed"
    else:
        print("Invalid choice.")
        return

    try:
        record = adherence_service.record_dose(
            patient_id=patient_id,
            medication_id=med_id,
            dose_date=dose_date,
            status=status
        )
        print(f"\nDose recorded: {status} on {dose_date}")
    except ValueError as e:
        print(f"\nError: {e}")


def _view_adherence(user, data_manager, services):
    """Display adherence summary for the logged-in patient."""
    patient_id = user["patient_id"]
    adherence_service = services["adherence"]

    # Get per-medication breakdown
    medications = data_manager.load_data("medications.json") or []
    treatments = services["treatment"].get_patient_treatments(patient_id)

    patient_meds = []
    for t in treatments:
        patient_meds.extend([
            m for m in medications
            if m.get("treatment_id") == t.get("treatment_id")
        ])

    print(f"\n--- Your Adherence Summary ---")

    overall_pct = adherence_service.calculate_adherence(patient_id)
    missed_count = adherence_service.count_missed_doses(patient_id)

    print(f"  Overall adherence : {overall_pct}%")
    print(f"  Total missed doses: {missed_count}")

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


def _symptom_checkin(user, data_manager, services):
    """Record a symptom check-in for the logged-in patient."""
    patient_id = user["patient_id"]
    symptom_service = services["symptom"]

    print("\n--- Symptom Check-In ---")

    valid_symptoms = ["cough", "fever", "night_sweats", "fatigue", "other"]
    print("Available symptoms:")
    for i, s in enumerate(valid_symptoms, 1):
        print(f"  {i}. {s}")

    print("Enter the numbers of your symptoms (comma-separated).")
    print("Example: 1,2")
    selection = input("Your selection: ").strip()

    chosen = []
    try:
        indices = [int(x.strip()) for x in selection.split(",")]
        for idx in indices:
            if 1 <= idx <= len(valid_symptoms):
                chosen.append(valid_symptoms[idx - 1])
            else:
                print(f"Invalid selection: {idx}")
                return
    except ValueError:
        print("Invalid input. Use comma-separated numbers.")
        return

    if not chosen:
        print("You must select at least one symptom.")
        return

    other_symptom = None
    if "other" in chosen:
        other_symptom = input("Describe the other symptom: ").strip()
        if not other_symptom:
            print("Description is required for 'other' symptom.")
            return

    severity = None
    print("\nSeverity level:")
    print("1. Mild")
    print("2. Moderate")
    print("3. Severe")
    sev_choice = input("Enter choice (or press Enter to skip): ").strip()
    if sev_choice == "1":
        severity = "mild"
    elif sev_choice == "2":
        severity = "moderate"
    elif sev_choice == "3":
        severity = "severe"

    notes = input("Any additional notes (or press Enter to skip): ").strip()
    if not notes:
        notes = None

    checkin_date = date.today().isoformat()

    try:
        record = symptom_service.record_symptom_checkin(
            patient_id=patient_id,
            checkin_date=checkin_date,
            symptoms=chosen,
            other_symptom=other_symptom,
            severity=severity,
            notes=notes
        )
        print(f"\nSymptom check-in recorded for {checkin_date}.")
    except ValueError as e:
        print(f"\nError: {e}")


def _view_symptom_history(user, data_manager, services):
    """Display the symptom history for the logged-in patient."""
    patient_id = user["patient_id"]
    symptom_service = services["symptom"]

    history = symptom_service.get_patient_history(patient_id)

    if not history:
        print("\nNo symptom check-ins on record.")
        return

    print(f"\n--- Your Symptom History ---")
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


def _request_refill(user, data_manager, services):
    """Request a medication refill for the logged-in patient."""
    patient_id = user["patient_id"]

    # Show the patient's medications
    medications = data_manager.load_data("medications.json") or []
    treatments = services["treatment"].get_patient_treatments(patient_id)

    patient_meds = []
    for t in treatments:
        patient_meds.extend([
            m for m in medications
            if m.get("treatment_id") == t.get("treatment_id")
        ])

    if not patient_meds:
        print("\nYou have no medications to request a refill for.")
        return

    print("\n--- Request Refill ---")
    print("Your medications:")
    for m in patient_meds:
        print(f"  [{m.get('medication_id')}] {m.get('name')} "
              f"(Remaining: {m.get('quantity')})")

    med_id_input = input("Enter medication ID to request refill: ").strip()
    try:
        med_id = int(med_id_input)
    except ValueError:
        print("Invalid medication ID.")
        return

    selected_med = None
    for m in patient_meds:
        if m.get("medication_id") == med_id:
            selected_med = m
            break

    if selected_med is None:
        print("That medication does not belong to you.")
        return

    # Check supply level first
    refill_service = services["refill"]
    remaining = refill_service.calculate_remaining_supply(
        selected_med.get("quantity", 0)
    )
    threshold = 30

    is_low = refill_service.check_supply(remaining, threshold)

    if not is_low:
        print(f"\nYour supply of {selected_med.get('name')} "
              f"is still sufficient ({remaining} remaining).")
        confirm = input("Request refill anyway? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Refill request cancelled.")
            return

    # Attempt to request refill
    try:
        request = refill_service.request_refill()
        print(f"\nRefill request submitted!")
        print(f"  Request ID : {request.get('request_id')}")
        print(f"  Medication  : {selected_med.get('name')}")
        print(f"  Status      : {request.get('status')}")
        print(f"  Date        : {request.get('date')}")
    except ValueError as e:
        print(f"\nError: {e}")


def _view_refill_status(user, data_manager, services):
    """View the status of refill requests."""
    refill_service = services["refill"]

    # Get all requests from the refill manager
    requests = refill_service.refill_manager.requests

    patient_requests = {
        k: v for k, v in requests.items()
        if v.get("patient_id") == user["patient_id"]
    }

    if not patient_requests:
        print("\nYou have no refill requests on record.")
        return

    print(f"\n--- Your Refill Requests ---")
    for req_id, req in patient_requests.items():
        print(f"  Request ID  : {req.get('request_id')}")
        print(f"  Medication ID: {req.get('medication_id')}")
        print(f"  Status      : {req.get('status')}")
        print(f"  Date        : {req.get('date')}")
        print("  " + "-" * 35)


def patient_menu(user, data_manager, services):
    """
    Run the patient menu loop.

    Parameters:
        user (dict): The logged-in patient user dict.
        data_manager (DataManager): For JSON persistence.
        services (dict): Dict of service instances.
    """
    while True:
        _display_patient_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            _view_treatment(user, data_manager, services)
        elif choice == "2":
            _view_medications(user, data_manager, services)
        elif choice == "3":
            _record_dose(user, data_manager, services)
        elif choice == "4":
            _view_adherence(user, data_manager, services)
        elif choice == "5":
            _symptom_checkin(user, data_manager, services)
        elif choice == "6":
            _view_symptom_history(user, data_manager, services)
        elif choice == "7":
            _request_refill(user, data_manager, services)
        elif choice == "8":
            _view_refill_status(user, data_manager, services)
        elif choice == "9":
            print(f"\nLogged out. Goodbye, {user.get('name', 'patient')}!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")
