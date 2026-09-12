from datetime import timedelta

class Treatment:
    def __init__(self, treatment_id, patient_id, start_date, duration_days, instructions ):
        if patient_id is None:
            raise ValueError("Patient ID is required")

        if duration_days <= 0:
            raise ValueError("Duration must be positive")

        self.treatment_id = treatment_id
        self.patient_id = patient_id
        self.start_date = start_date
        self.duration_days = duration_days
        self.instructions = instructions
        self.status = "active"

    def get_details(self):
        return {
            "treatment_id": self.treatment_id,
            "patient_id": self.patient_id,
            "start_date": self.start_date,
            "duration_days": self.duration_days,
            "status": self.status
        }

    def get_end_date(self):
        return self.start_date + timedelta(days=self.duration_days)

    def update_status(self, status):
        if status not in ["active", "completed"]:
            raise ValueError("Invalid status")

        self.status = status

    def update_instructions(self, instructions):
        self.instructions = instructions