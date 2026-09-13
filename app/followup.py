from datetime import date


class FollowUpTracker:
    VALID_STATUSES = {
        "open",
        "in_progress",
        "completed",
        "escalated"
    }

    def __init__(self, healthworker_id):
        if healthworker_id is None:
            raise ValueError("Healthworker is required")

        self.healthworker_id = healthworker_id
        self.cases = []
        self.next_case_id = 1

    def get_cases(self):
        return self.cases

    def create_case(self, patient_id, reason):
        if patient_id is None:
            raise ValueError("Patient is required")

        if not reason:
            raise ValueError("Follow-up reason is required")

        case = {
            "case_id": self.next_case_id,
            "patient_id": patient_id,
            "healthworker_id": self.healthworker_id,
            "reason": reason,
            "status": "open",
            "created_date": date.today(),
            "action": None,
            "escalation_reason": None
        }

        self.cases.append(case)
        self.next_case_id += 1

        return case

    def get_case(self, case_id):
        for case in self.cases:
            if case["case_id"] == case_id:
                return case

        return None

    def update_case(self, case_id, action):
        case = self.get_case(case_id)

        if case is None:
            raise ValueError("Follow-up case not found")

        case["action"] = action

        return case

    def update_status(self, case_id, status):
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid follow-up status")

        case = self.get_case(case_id)

        if case is None:
            raise ValueError("Follow-up case not found")

        case["status"] = status

        return case

    def get_patient_cases(self, patient_id):
        return [
            case
            for case in self.cases
            if case["patient_id"] == patient_id
        ]

    def get_open_cases(self):
        return [
            case
            for case in self.cases
            if case["status"] == "open"
        ]

    def escalate_case(self, case_id, reason):
        case = self.get_case(case_id)

        if case is None:
            raise ValueError("Follow-up case not found")

        case["status"] = "escalated"
        case["escalation_reason"] = reason

        return case