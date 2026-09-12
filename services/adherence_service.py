from datetime import date
from typing import Optional

from app.adherence import AdherenceTracker


class AdherenceService:
    """
    Coordinates adherence operations between the CLI, AdherenceTracker
    domain object, and JSON persistence layer.
    """

    FILE_NAME = "adherence.json"

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def _load_records(self) -> list:
        """Load adherence records from JSON."""
        records = self.data_manager.load(self.FILE_NAME)
        return records if records is not None else []

    def _save_records(self, records: list) -> None:
        """Save adherence records to JSON."""
        self.data_manager.save(self.FILE_NAME, records)

    @staticmethod
    def _format_date(value) -> str:
        """Convert date or datetime values into JSON-safe strings."""
        if hasattr(value, "isoformat"):
            return value.isoformat()

        return str(value)

    @staticmethod
    def _record_to_dict(record) -> dict:
        """Convert an adherence record object into a dictionary."""
        if hasattr(record, "to_dict"):
            return record.to_dict()

        return {
            "record_id": getattr(record, "record_id", None),
            "patient_id": getattr(record, "patient_id", None),
            "medication_id": getattr(record, "medication_id", None),
            "date": AdherenceService._format_date(
                getattr(record, "date", None)
            ),
            "status": getattr(record, "status", None),
        }

    def _create_tracker(self, patient_id: str, medication_id: str):
        """
        Create an AdherenceTracker.

        Adjust these arguments if your AdherenceTracker constructor
        uses different parameter names.
        """
        return AdherenceTracker(
            patient_id=patient_id,
            medication_id=medication_id,
        )

    def record_dose(
        self,
        patient_id: str,
        medication_id: str,
        dose_date,
        status: str,
        record_id: Optional[str] = None,
    ) -> dict:
        """
        Record a taken or missed dose.

        Valid statuses:
            taken
            missed
        """
        status = status.lower().strip()

        if status not in {"taken", "missed"}:
            raise ValueError("Dose status must be 'taken' or 'missed'.")

        if not patient_id:
            raise ValueError("patient_id is required.")

        if not medication_id:
            raise ValueError("medication_id is required.")

        records = self._load_records()

        date_string = self._format_date(dose_date)

        duplicate_exists = any(
            record.get("patient_id") == patient_id
            and record.get("medication_id") == medication_id
            and record.get("date") == date_string
            for record in records
        )

        if duplicate_exists:
            raise ValueError(
                "A dose record already exists for this patient, "
                "medication, and date."
            )

        tracker = self._create_tracker(patient_id, medication_id)

        # Use the domain object's behaviour if these methods exist.
        if status == "taken" and hasattr(tracker, "record_taken"):
            record = tracker.record_taken(dose_date)
        elif status == "missed" and hasattr(tracker, "record_missed"):
            record = tracker.record_missed(dose_date)
        else:
            record = {
                "record_id": record_id,
                "patient_id": patient_id,
                "medication_id": medication_id,
                "date": date_string,
                "status": status,
            }

        if isinstance(record, dict):
            record.setdefault("record_id", record_id)
            record.setdefault("patient_id", patient_id)
            record.setdefault("medication_id", medication_id)
            record.setdefault("date", date_string)
            record.setdefault("status", status)
            record_dict = record
        else:
            record_dict = self._record_to_dict(record)

        records.append(record_dict)
        self._save_records(records)

        return record_dict

    def get_patient_history(
        self,
        patient_id: str,
        medication_id: Optional[str] = None,
    ) -> list:
        """Return adherence records for a patient."""
        records = self._load_records()

        patient_records = [
            record
            for record in records
            if record.get("patient_id") == patient_id
        ]

        if medication_id is not None:
            patient_records = [
                record
                for record in patient_records
                if record.get("medication_id") == medication_id
            ]

        return patient_records

    def get_missed_doses(
        self,
        patient_id: str,
        medication_id: Optional[str] = None,
    ) -> list:
        """Return missed-dose records for a patient."""
        history = self.get_patient_history(patient_id, medication_id)

        return [
            record
            for record in history
            if record.get("status") == "missed"
        ]

    def calculate_adherence(
        self,
        patient_id: str,
        medication_id: Optional[str] = None,
    ) -> float:
        """
        Calculate adherence percentage.

        Formula:
            taken doses / total recorded doses * 100
        """
        history = self.get_patient_history(patient_id, medication_id)

        if not history:
            return 0.0

        taken_doses = sum(
            1 for record in history if record.get("status") == "taken"
        )

        return round((taken_doses / len(history)) * 100, 2)

    def count_missed_doses(
        self,
        patient_id: str,
        medication_id: Optional[str] = None,
    ) -> int:
        """Return the number of missed doses."""
        return len(self.get_missed_doses(patient_id, medication_id))
