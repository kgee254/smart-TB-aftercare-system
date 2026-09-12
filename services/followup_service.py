from app.followup import FollowUpTracker


class FollowUpService:
    def __init__(self):
        self.trackers = {}

    def create_tracker(self, healthworker_id):
        tracker = FollowUpTracker(healthworker_id)

        self.trackers[healthworker_id] = tracker

        return tracker

    def get_tracker(self, healthworker_id):
        return self.trackers.get(healthworker_id)

    def create_case(self, healthworker_id, patient_id, reason):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            tracker = self.create_tracker(healthworker_id)

        return tracker.create_case(
            patient_id=patient_id,
            reason=reason
        )

    def get_cases(self, healthworker_id):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            return []

        return tracker.get_cases()

    def get_case(self, healthworker_id, case_id):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            return None

        return tracker.get_case(case_id)

    def update_case(self, healthworker_id, case_id, action):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            raise ValueError("Healthworker tracker not found")

        return tracker.update_case(
            case_id=case_id,
            action=action
        )

    def update_status(self, healthworker_id, case_id, status):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            raise ValueError("Healthworker tracker not found")

        return tracker.update_status(
            case_id=case_id,
            status=status
        )

    def get_patient_cases(self, healthworker_id, patient_id):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            return []

        return tracker.get_patient_cases(patient_id)

    def get_open_cases(self, healthworker_id):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            return []

        return tracker.get_open_cases()

    def escalate_case(self, healthworker_id, case_id, reason):
        tracker = self.get_tracker(healthworker_id)

        if tracker is None:
            raise ValueError("Healthworker tracker not found")

        return tracker.escalate_case(
            case_id=case_id,
            reason=reason
        )