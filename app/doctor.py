class Doctor:

    def __init__(
        self,
        doctor_id,
        name,
        username,
        password,
        phone,
        specialization
    ):
        if not name:
            raise ValueError("Doctor name cannot be empty.")

        self.doctor_id = doctor_id
        self.name = name
        self.username = username
        self.password = password
        self.phone = phone
        self.specialization = specialization
        self.role = "doctor"

    def get_profile(self):
        return {
            "doctor_id": self.doctor_id,
            "name": self.name,
            "username": self.username,
            "phone": self.phone,
            "specialization": self.specialization
        }

    def view_patient(self, patient_id, patients):
        for patient in patients:
            if patient["patient_id"] == patient_id:
                return patient

        return None

    def record_clinical_note(self, patient_id, note):
        return {
            "patient_id": patient_id,
            "doctor_id": self.doctor_id,
            "note": note
        }