class Patient:

    def __init__(
        self,
        patient_id,
        name,
        username,
        password,
        phone
    ):
        if not name:
            raise ValueError("Patient name cannot be empty.")

        if not username:
            raise ValueError("Patient username cannot be empty.")

        self.patient_id = patient_id
        self.name = name
        self.username = username
        self.password = password
        self.phone = phone
        self.role = "patient"

    def get_profile(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "username": self.username,
            "phone": self.phone
        }

    def update_phone(self, new_phone):
        self.phone = new_phone