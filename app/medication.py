class Medication:
    def __init__(
        self,
        medication_id,
        treatment_id,
        name,
        dosage,
        frequency,
        quantity,
        duration_days,
        instructions
    ):
        if treatment_id is None:
            raise ValueError("Treatment ID is required")

        if dosage <= 0:
            raise ValueError("Dosage must be positive")

        if frequency <= 0:
            raise ValueError("Frequency must be positive")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if duration_days <= 0:
            raise ValueError("Duration must be positive")

        self.medication_id = medication_id
        self.treatment_id = treatment_id
        self.name = name
        self.dosage = dosage
        self.frequency = frequency
        self.quantity = quantity
        self.duration_days = duration_days
        self.instructions = instructions

    def get_details(self):
        return {
            "medication_id": self.medication_id,
            "treatment_id": self.treatment_id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "quantity": self.quantity,
            "duration_days": self.duration_days,
            "instructions": self.instructions
        }

    def update_instructions(self, instructions):
        self.instructions = instructions

    def record_dose(self):
        if self.quantity > 0:
            self.quantity -= 1

    def get_remaining_quantity(self):
        return self.quantity