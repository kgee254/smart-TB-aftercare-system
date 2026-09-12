from models.refill import RefillRequest


class RefillService:
    """
    Handles creation and management of medication refill requests.
    """

    def __init__(self, storage):
        self.storage = storage
        self.refills = []

    def load_refills(self):
        """Load refill requests from storage."""
        data = self.storage.load("refills.json")

        self.refills = [
            RefillRequest.from_dict(item)
            for item in data
        ]

        return self.refills

    def save_refills(self):
        """Save refill requests to storage."""
        data = [refill.to_dict() for refill in self.refills]
        self.storage.save("refills.json", data)

    def create_request(self, patient_id, medication_id):
        """Create a new refill request."""

        request_id = self._generate_id()

        refill = RefillRequest(
            request_id=request_id,
            patient_id=patient_id,
            medication_id=medication_id
        )

        self.refills.append(refill)
        self.save_refills()

        return refill

    def get_request(self, request_id):
        """Find a refill request by ID."""

        for refill in self.refills:
            if refill.request_id == request_id:
                return refill

        return None

    def get_patient_requests(self, patient_id):
        """Return all refill requests belonging to a patient."""

        return [
            refill
            for refill in self.refills
            if refill.patient_id == patient_id
        ]

    def get_pending_requests(self):
        """Return refill requests waiting for staff action."""

        return [
            refill
            for refill in self.refills
            if refill.status == "pending"
        ]

    def approve_request(self, request_id):
        """Approve a refill request."""

        refill = self.get_request(request_id)

        if refill is None:
            raise ValueError("Refill request not found.")

        refill.approve()
        self.save_refills()

        return refill

    def reject_request(self, request_id):
        """Reject a refill request."""

        refill = self.get_request(request_id)

        if refill is None:
            raise ValueError("Refill request not found.")

        refill.reject()
        self.save_refills()

        return refill

    def complete_request(self, request_id):
        """Complete an approved refill request."""

        refill = self.get_request(request_id)

        if refill is None:
            raise ValueError("Refill request not found.")

        refill.complete()
        self.save_refills()

        return refill

    def _generate_id(self):
        """Generate the next refill request ID."""

        if not self.refills:
            return 1

        return max(
            refill.request_id for refill in self.refills
        ) + 1