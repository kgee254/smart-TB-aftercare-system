from datetime import date


class SymptomTracker:
    VALID_SYMPTOMS = {
        "cough",
        "fever",
        "night_sweats",
        "fatigue",
        "other"
    }

    VALID_SEVERITIES = {
        "mild",
        "moderate",
        "severe"
    }

    def __init__(self, patient_id):
        if patient_id is None:
            raise ValueError("Patient ID is required")

        self.patient_id = patient_id
        self.history = []

    def get_history(self):
        return self.history

    def record_checkin(
        self,
        checkin_date,
        symptoms,
        other_symptom=None,
        severity=None,
        notes=None
    ):
        # Validate symptoms
        for symptom in symptoms:
            if symptom not in self.VALID_SYMPTOMS:
                raise ValueError(f"Invalid symptom: {symptom}")

        # "other" requires a description
        if "other" in symptoms and not other_symptom:
            raise ValueError(
                "Other symptom requires a description"
            )

        # Validate severity
        if severity is not None:
            if severity not in self.VALID_SEVERITIES:
                raise ValueError("Invalid symptom severity")

        # Prevent duplicate check-in dates
        for record in self.history:
            if record["date"] == checkin_date:
                raise ValueError(
                    "A check-in already exists for this date"
                )

        record = {
            "patient_id": self.patient_id,
            "date": checkin_date,
            "symptoms": symptoms,
            "other_symptom": other_symptom,
            "severity": severity,
            "notes": notes
        }

        self.history.append(record)

        return record

