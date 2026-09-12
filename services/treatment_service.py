from datetime import date
from typing import Optional

from app.treatment import Treatment


class TreatmentService:
    """
    Coordinates treatment operations between the CLI, Treatment domain
    object, and JSON persistence layer.
    """

    FILE_NAME = "treatments.json"

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def _load_treatments(self) -> list:
        """Load all treatment records from JSON."""
        records = self.data_manager.load(self.FILE_NAME)
        return records if records is not None else []

    def _save_treatments(self, treatments: list) -> None:
        """Save all treatment records to JSON."""
        self.data_manager.save(self.FILE_NAME, treatments)

    @staticmethod
    def _to_dict(treatment) -> dict:
        """
        Convert a Treatment object into a JSON-compatible dictionary.

        This supports either a to_dict() method or normal object attributes.
        """
        if hasattr(treatment, "to_dict"):
            return treatment.to_dict()

        return {
            "treatment_id": getattr(treatment, "treatment_id", None),
            "patient_id": getattr(treatment, "patient_id", None),
            "start_date": TreatmentService._format_date(
                getattr(treatment, "start_date", None)
            ),
            "duration_days": getattr(treatment, "duration_days", None),
            "end_date": TreatmentService._format_date(
                getattr(treatment, "end_date", None)
            ),
            "instructions": getattr(treatment, "instructions", ""),
            "status": getattr(treatment, "status", "active"),
        }

    @staticmethod
    def _format_date(value):
        """Convert date objects to strings for JSON storage."""
        if isinstance(value, date):
            return value.isoformat()

        return value

    def create_treatment(
        self,
        patient_id: str,
        start_date,
        duration_days: int,
        instructions: str = "",
        treatment_id: Optional[str] = None,
    ):
        """
        Create and persist a new treatment.

        Returns:
            Treatment: The newly created Treatment object.
        """
        if not patient_id:
            raise ValueError("patient_id is required.")

        if duration_days <= 0:
            raise ValueError("duration_days must be greater than zero.")

        if not instructions and instructions is not None:
            instructions = ""

        treatment_arguments = {
            "patient_id": patient_id,
            "start_date": start_date,
            "duration_days": duration_days,
            "instructions": instructions,
        }

        if treatment_id is not None:
            treatment_arguments["treatment_id"] = treatment_id

        treatment = Treatment(**treatment_arguments)

        treatments = self._load_treatments()
        treatments.append(self._to_dict(treatment))
        self._save_treatments(treatments)

        return treatment

    def get_all_treatments(self) -> list:
        """Return all stored treatment dictionaries."""
        return self._load_treatments()

    def get_treatment(self, treatment_id: str) -> Optional[dict]:
        """Find one treatment by ID."""
        if not treatment_id:
            return None

        treatments = self._load_treatments()

        for treatment in treatments:
            if treatment.get("treatment_id") == treatment_id:
                return treatment

        return None

    def get_patient_treatments(self, patient_id: str) -> list:
        """Return all treatments belonging to a patient."""
        if not patient_id:
            return []

        treatments = self._load_treatments()

        return [
            treatment
            for treatment in treatments
            if treatment.get("patient_id") == patient_id
        ]

    def complete_treatment(self, treatment_id: str) -> dict:
        """
        Mark a treatment as completed and persist the change.
        """
        treatments = self._load_treatments()

        for treatment in treatments:
            if treatment.get("treatment_id") == treatment_id:
                treatment["status"] = "completed"
                self._save_treatments(treatments)
                return treatment

        raise ValueError(f"Treatment '{treatment_id}' was not found.")

    def update_treatment(self, treatment_id: str, **updates) -> dict:
        """
        Update selected treatment fields.

        Example:
            service.update_treatment(
                "T001",
                instructions="Take after breakfast"
            )
        """
        allowed_fields = {
            "start_date",
            "duration_days",
            "end_date",
            "instructions",
            "status",
        }

        invalid_fields = set(updates) - allowed_fields

        if invalid_fields:
            raise ValueError(
                f"Cannot update fields: {', '.join(sorted(invalid_fields))}"
            )

        treatments = self._load_treatments()

        for treatment in treatments:
            if treatment.get("treatment_id") == treatment_id:
                treatment.update(updates)
                self._save_treatments(treatments)
                return treatment

        raise ValueError(f"Treatment '{treatment_id}' was not found.")
