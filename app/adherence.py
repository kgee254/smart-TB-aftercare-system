class AdherenceTracker:
    def __init__(self, patient_id, medication_id):
        if patient_id is None:
            raise ValueError("Patient ID is required")

        if medication_id is None:
            raise ValueError("Medication ID is required")

        self.patient_id = patient_id
        self.medication_id = medication_id
        self.history = []

    def record_dose(self, dose_date, status):
        if status not in ["taken", "missed"]:
            raise ValueError("Invalid adherence status")

        for record in self.history:
            if record["date"] == dose_date:
                raise ValueError("Dose already recorded for this date")

        self.history.append({
            "patient_id": self.patient_id,
            "medication_id": self.medication_id,
            "date": dose_date,
            "status": status
        })

    def get_history(self):
        return self.history

    def get_adherence_percentage(self):
        if not self.history:
            return 0

        taken_doses = sum(
            1 for record in self.history
            if record["status"] == "taken"
        )

        return (taken_doses / len(self.history)) * 100

    def get_missed_dose_count(self):
        return sum(
            1 for record in self.history
            if record["status"] == "missed"
        )