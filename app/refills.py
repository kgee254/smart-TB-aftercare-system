from datetime import datetime


class RefillRequest:
    """
    Represents a patient's request for more medication.
    """

    VALID_STATUSES = {"pending", "approved", "rejected", "completed"}

    def __init__(self, request_id, patient_id, medication_id, date=None,
                 status="pending"):
        self.request_id = request_id
        self.patient_id = patient_id
        self.medication_id = medication_id
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status

        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid refill status: {self.status}")

    def approve(self):
        """Approve a pending refill request."""
        if self.status != "pending":
            raise ValueError("Only pending refill requests can be approved.")

        self.status = "approved"

    def reject(self):
        """Reject a pending refill request."""
        if self.status != "pending":
            raise ValueError("Only pending refill requests can be rejected.")

        self.status = "rejected"

    def complete(self):
        """Mark an approved refill as completed."""
        if self.status != "approved":
            raise ValueError(
                "Only approved refill requests can be completed."
            )

        self.status = "completed"

    def to_dict(self):
        """Convert the refill request into JSON-compatible data."""
        return {
            "request_id": self.request_id,
            "patient_id": self.patient_id,
            "medication_id": self.medication_id,
            "status": self.status,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data):
        """Create a RefillRequest object from stored JSON data."""
        return cls(
            request_id=data["request_id"],
            patient_id=data["patient_id"],
            medication_id=data["medication_id"],
            status=data.get("status", "pending"),
            date=data.get("date")
        )

    def __str__(self):
        return (
            f"Refill Request #{self.request_id} | "
            f"Patient: {self.patient_id} | "
            f"Medication: {self.medication_id} | "
            f"Status: {self.status} | "
            f"Date: {self.date}"
        )