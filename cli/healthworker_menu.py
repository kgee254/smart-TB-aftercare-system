from datetime import date


def _display_healthworker_menu():
    """Display the health worker menu options."""
    print("\n" + "=" * 50)
    print("   HEALTH WORKER MENU")
    print("=" * 50)
    print("1. View assigned patients")
    print("2. View a patient's details")
    print("3. Monitor patient adherence")
    print("4. Review patient symptoms")
    print("5. View refill requests")
    print("6. Create follow-up case")
    print("7. View my follow-up cases")
    print("8. Update follow-up case")
    print("9. Escalate a case")
    print("10. View patients needing attention")
    print("11. Logout")
    print("=" * 50)


def _view_assigned_patients(user, data_manager, services):
    """Display all patients assigned to this health worker."""
    assigned_ids = user.get("assigned_patients", [])
    patients = data_manager.load_data("patients.json") or []

    assigned = [
        p for p in patients
        if p.get("patient_id") in assigned_ids
    ]

    if not assigned:
        print("\nYou have no assigned patients.")
        return

    print(f"\n--- Your Assigned Patients ({len(assigned)}) ---")
    for p in assigned:
        attention = " ⚠ NEEDS ATTENTION" if p.get("needs_attention") else ""
        print(f"  ID: {p.get('patient_id')}  "
              f"Name: {p.get('name')}  "
              f"Phone: {p.get('phone')}{attention}")


def _view_patient_details(user, data_manager, services):
    """View details of a specific assigned patient."""
    assigned_ids = user.get("assigned_patients", [])
    patients = data_manager.load_data("patients.json") or []

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    if patient_id not in assigned_ids:
        print("This patient is not assigned to you.")
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
    print(f"  Phone       : {patient.get('phone')}")
    print(f"  Attention   : {'Yes' if patient.get('needs_attention') else 'No'}")

    # Show their treatments
    treatments = services["treatment"].get_patient_treatments(patient_id)
    if treatments:
        print(f"  Treatments  : {len(treatments)}")
        for t in treatments:
            print(f"    - T{t.get('treatment_id')}: "
                  f"{t.get('status')} "
                  f"(started {t.get('start_date')})")


def _monitor_adherence(user, data_manager, services):
    """Monitor adherence for an assigned patient."""
    assigned_ids = user.get("assigned_patients", [])
    adherence_service = services["adherence"]

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    if patient_id not in assigned_ids:
        print("This patient is not assigned to you.")
        return

    overall_pct = adherence_service.calculate_adherence(patient_id)
    missed = adherence_service.count_missed_doses(patient_id)

    print(f"\n--- Adherence for Patient {patient_id} ---")
    print(f"  Overall adherence : {overall_pct}%")
    print(f"  Total missed     : {missed} doses")

    if overall_pct < 80 and overall_pct > 0:
        print("  ⚠ Adherence is below 80% — follow-up recommended.")
    elif overall_pct == 0:
        print("  ⚠ No adherence data recorded yet.")

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


def _review_symptoms(user, data_manager, services):
    """Review symptom history for an assigned patient."""
    assigned_ids = user.get("assigned_patients", [])
    symptom_service = services["symptom"]

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    if patient_id not in assigned_ids:
        print("This patient is not assigned to you.")
        return

    history = symptom_service.get_patient_history(patient_id)

    if not history:
        print(f"\nNo symptom records for patient {patient_id}.")
        return

    print(f"\n--- Symptom History for Patient {patient_id} ---")
    for record in history:
        severity = record.get('severity', 'unknown')
        if severity == 'severe':
            severity_display = "SEVERE ⚠"
        elif severity == 'moderate':
            severity_display = "moderate"
        else:
            severity_display = severity

        print(f"  Date       : {record.get('date')}")
        print(f"  Symptoms   : {', '.join(record.get('symptoms', []))}")
        if record.get('other_symptom'):
            print(f"  Other      : {record.get('other_symptom')}")
        print(f"  Severity   : {severity_display}")
        if record.get('notes'):
            print(f"  Notes      : {record.get('notes')}")
        print("  " + "-" * 35)


def _view_refill_requests(user, data_manager, services):
    """View all refill requests for assigned patients."""
    refill_service = services["refill"]

    requests = refill_service.refill_manager.requests

    assigned_ids = user.get("assigned_patients", [])

    assigned_requests = {
        k: v for k, v in requests.items()
        if v.get("patient_id") in assigned_ids
    }

    if not assigned_requests:
        print("\nNo refill requests for your assigned patients.")
        return

    print(f"\n--- Refill Requests ({len(assigned_requests)}) ---")

    for req_id, req in assigned_requests.items():
        status = req.get('status', 'unknown')
        print(f"  Request ID   : {req.get('request_id')}")
        print(f"  Patient ID   : {req.get('patient_id')}")
        print(f"  Medication ID: {req.get('medication_id')}")
        print(f"  Status       : {status}")
        print(f"  Date         : {req.get('date')}")

        if status == "requested":
            print("  → Action needed: process this request.")

        print("  " + "-" * 35)


def _create_followup_case(user, data_manager, services):
    """Create a new follow-up case for a patient."""
    followup_service = services["followup"]
    assigned_ids = user.get("assigned_patients", [])

    print("\n--- Create Follow-Up Case ---")

    patient_id_input = input("Enter patient ID: ").strip()
    try:
        patient_id = int(patient_id_input)
    except ValueError:
        print("Invalid patient ID.")
        return

    if patient_id not in assigned_ids:
        print("This patient is not assigned to you.")
        return

    reason = input("Reason for follow-up: ").strip()
    if not reason:
        print("Reason is required.")
        return

    healthworker_id = user.get("healthworker_id")

    try:
        case = followup_service.create_case(
            healthworker_id=healthworker_id,
            patient_id=patient_id,
            reason=reason
        )
        print(f"\nFollow-up case created!")
        print(f"  Case ID   : {case.get('case_id')}")
        print(f"  Patient   : {patient_id}")
        print(f"  Reason    : {reason}")
        print(f"  Status    : {case.get('status')}")
    except ValueError as e:
        print(f"\nError: {e}")


def _view_followup_cases(user, data_manager, services):
    """View all follow-up cases for this health worker."""
    followup_service = services["followup"]
    healthworker_id = user.get("healthworker_id")

    cases = followup_service.get_cases(healthworker_id)

    if not cases:
        print("\nYou have no follow-up cases.")
        return

    print(f"\n--- Your Follow-Up Cases ({len(cases)}) ---")
    for case in cases:
        status = case.get('status', 'unknown')
        if status == 'escalated':
            status_display = "ESCALATED ⚠"
        elif status == 'open':
            status_display = "open → action needed"
        else:
            status_display = status

        print(f"  Case ID    : {case.get('case_id')}")
        print(f"  Patient ID : {case.get('patient_id')}")
        print(f"  Reason     : {case.get('reason')}")
        print(f"  Status     : {status_display}")
        if case.get('action'):
            print(f"  Action     : {case.get('action')}")
        if case.get('escalation_reason'):
            print(f"  Escalation : {case.get('escalation_reason')}")
        print("  " + "-" * 35)


def _update_followup_case(user, data_manager, services):
    """Update a follow-up case with an action and/or status change."""
    followup_service = services["followup"]
    healthworker_id = user.get("healthworker_id")

    print("\n--- Update Follow-Up Case ---")

    case_id_input = input("Enter case ID: ").strip()
    try:
        case_id = int(case_id_input)
    except ValueError:
        print("Invalid case ID.")
        return

    # Verify case exists
    case = followup_service.get_case(healthworker_id, case_id)
    if case is None:
        print(f"Case {case_id} not found among your cases.")
        return

    print("What would you like to do?")
    print("1. Record an action")
    print("2. Update case status")
    print("3. Both")
    sub_choice = input("Enter choice: ").strip()

    action = None
    status = None

    if sub_choice in ("1", "3"):
        action = input("Describe the action taken: ").strip()
        if not action:
            print("Action cannot be empty.")
            return

    if sub_choice in ("2", "3"):
        print("Valid statuses: open, in_progress, completed")
        status = input("Enter new status: ").strip().lower()
        if status not in ("open", "in_progress", "completed"):
            print("Invalid status.")
            return

    try:
        if action:
            followup_service.update_case(
                healthworker_id, case_id, action
            )
        if status:
            followup_service.update_status(
                healthworker_id, case_id, status
            )
        print(f"\nCase {case_id} updated successfully.")
    except ValueError as e:
        print(f"\nError: {e}")


def _escalate_case(user, data_manager, services):
    """Escalate a follow-up case to a doctor."""
    followup_service = services["followup"]
    healthworker_id = user.get("healthworker_id")

    print("\n--- Escalate Case ---")

    case_id_input = input("Enter case ID to escalate: ").strip()
    try:
        case_id = int(case_id_input)
    except ValueError:
        print("Invalid case ID.")
        return

    # Verify case exists
    case = followup_service.get_case(healthworker_id, case_id)
    if case is None:
        print(f"Case {case_id} not found among your cases.")
        return

    if case.get('status') == 'escalated':
        print("This case is already escalated.")
        return

    reason = input("Reason for escalation: ").strip()
    if not reason:
        print("Escalation reason is required.")
        return

    confirm = input(
        f"Confirm escalating case {case_id}? (yes/no): "
    ).strip().lower()

    if confirm != "yes":
        print("Escalation cancelled.")
        return

    try:
        escalated = followup_service.escalate_case(
            healthworker_id, case_id, reason
        )
        print(f"\nCase {case_id} has been escalated!")
        print(f"  Reason: {reason}")
    except ValueError as e:
        print(f"\nError: {e}")


def _view_patients_needing_attention(user, data_manager, services):
    """Display patients flagged as needing attention."""
    assigned_ids = user.get("assigned_patients", [])
    patients = data_manager.load_data("patients.json") or []

    needing_attention = [
        p for p in patients
        if p.get("patient_id") in assigned_ids
        and p.get("needs_attention") is True
    ]

    if not needing_attention:
        print("\nNo patients currently flagged as needing attention.")
        return

    print(f"\n--- Patients Needing Attention ({len(needing_attention)}) ⚠ ---")
    for p in needing_attention:
        print(f"  ID: {p.get('patient_id')}  "
              f"Name: {p.get('name')}  "
              f"Phone: {p.get('phone')}")

        # Show why they need attention
        adherence_service = services["adherence"]
        adherence_pct = adherence_service.calculate_adherence(
            p.get("patient_id")
        )
        missed = adherence_service.count_missed_doses(
            p.get("patient_id")
        )
        print(f"       Adherence: {adherence_pct}%, "
              f"Missed doses: {missed}")


def healthworker_menu(user, data_manager, services):
    """
    Run the health worker menu loop.

    Parameters:
        user (dict): The logged-in health worker user dict.
        data_manager (DataManager): For JSON persistence.
        services (dict): Dict of service instances.
    """
    while True:
        _display_healthworker_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            _view_assigned_patients(user, data_manager, services)
        elif choice == "2":
            _view_patient_details(user, data_manager, services)
        elif choice == "3":
            _monitor_adherence(user, data_manager, services)
        elif choice == "4":
            _review_symptoms(user, data_manager, services)
        elif choice == "5":
            _view_refill_requests(user, data_manager, services)
        elif choice == "6":
            _create_followup_case(user, data_manager, services)
        elif choice == "7":
            _view_followup_cases(user, data_manager, services)
        elif choice == "8":
            _update_followup_case(user, data_manager, services)
        elif choice == "9":
            _escalate_case(user, data_manager, services)
        elif choice == "10":
            _view_patients_needing_attention(user, data_manager, services)
        elif choice == "11":
            print(f"\nLogged out. Goodbye, {user.get('name', 'Health Worker')}!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 11.")
