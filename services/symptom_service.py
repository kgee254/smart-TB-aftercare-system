from app.symptoms import SymptomTracker


class SymptomService:
    def __init__(self):
        self.trackers = {}

    def create_tracker(self, patient_id):
        tracker = SymptomTracker(patient_id)
        self.trackers[patient_id] = tracker
        return tracker

    def get_tracker(self, patient_id):
        return self.trackers.get(patient_id)

    def record_symptom_checkin(
        self,
        patient_id,
        checkin_date,
        symptoms,
        other_symptom=None,
        severity=None,
        notes=None
    ):
        tracker = self.get_tracker(patient_id)

        if tracker is None:
            tracker = self.create_tracker(patient_id)

        return tracker.record_checkin(
            checkin_date=checkin_date,
            symptoms=symptoms,
            other_symptom=other_symptom,
            severity=severity,
            notes=notes
        )

    def get_patient_history(self, patient_id):
        tracker = self.get_tracker(patient_id)

        if tracker is None:
            return []

        return tracker.get_history()

