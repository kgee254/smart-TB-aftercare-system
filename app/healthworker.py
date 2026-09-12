class HealthWorker:

    def __init__(
        self,
        healthworker_id,
        name,
        username,
        password,
        phone
    ):
        if not name:
            raise ValueError("Healthworker name cannot be empty.")

        self.healthworker_id = healthworker_id
        self.name = name
        self.username = username
        self.password = password
        self.phone = phone
        self.role = "healthworker"
        self.assigned_patients = []

    def get_profile(self):
        return {
            "healthworker_id": self.healthworker_id,
            "name": self.name,
            "username": self.username,
            "phone": self.phone
        }

    def assign_patient(self, patient_id):
        if patient_id not in self.assigned_patients:
            self.assigned_patients.append(patient_id)

    def view_assigned_patients(self, patients):
        assigned = []

        for patient in patients:
            if patient["patient_id"] in self.assigned_patients:
                assigned.append(patient)

        return assigned

    def view_patient(self, patient_id, patients):
        if patient_id not in self.assigned_patients:
            return None

        for patient in patients:
            if patient["patient_id"] == patient_id:
                return patient

        return None

    def get_patients_needing_attention(self, patients):
        patients_needing_attention = []

        for patient in patients:
            if (
                patient["patient_id"] in self.assigned_patients
                and patient["needs_attention"] is True
            ):
                patients_needing_attention.append(patient)

        return patients_needing_attention

    def record_followup(self, patient_id, action):
        return {
            "healthworker_id": self.healthworker_id,
            "patient_id": patient_id,
            "action": action
        }