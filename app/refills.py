from datetime import date


class RefillManager:
    """
    Manages medication supply and refill requests for a patient.
    """

    VALID_STATUSES = {
        "requested",
        "in_progress",
        "completed",
        "rejected",
    }

    def __init__(
        self,
        patient_id,
        medication_id,
        quantity,
        frequency,
        start_date
    ):
        if patient_id is None:
            raise ValueError("patient_id is required")

        if medication_id is None:
            raise ValueError("medication_id is required")

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if frequency <= 0:
            raise ValueError("frequency must be positive")

        self.patient_id = patient_id
        self.medication_id = medication_id
        self.quantity = quantity
        self.frequency = frequency
        self.start_date = start_date

        # Stores refill requests created by this manager.
        self.requests = {}

        # Used to generate unique request IDs.
        self._next_request_id = 1

    def calculate_remaining_quantity(self, doses_taken):
        """
        Calculate how much medication remains.

        Remaining quantity cannot be negative.
        """
        remaining = self.quantity - doses_taken

        return max(remaining, 0)

    def is_supply_low(self, remaining_quantity, threshold):
        """
        Return True when remaining medication is below the threshold.
        """
        return remaining_quantity < threshold

    def create_alert(self, remaining_quantity, threshold):
        """
        Create a low-medication alert if supply is below the threshold.
        """
        if not self.is_supply_low(remaining_quantity, threshold):
            return None

        return {
            "patient_id": self.patient_id,
            "medication_id": self.medication_id,
            "remaining_quantity": remaining_quantity,
            "threshold": threshold,
            "status": "active",
        }

    def request_refill(self):
        """
        Create a new refill request.

        Only one active refill request is allowed at a time.
        """
        for request in self.requests.values():
            if request["status"] in {"requested", "in_progress"}:
                raise ValueError(
                    "An active refill request already exists"
                )

        request_id = self._next_request_id
        self._next_request_id += 1

        request = {
            "request_id": request_id,
            "patient_id": self.patient_id,
            "medication_id": self.medication_id,
            "status": "requested",
            "date": date.today().isoformat(),
        }

        self.requests[request_id] = request

        return request

    def update_request_status(self, request_id, status):
        """
        Update the status of an existing refill request.
        """
        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid refill request status")

        if request_id not in self.requests:
            raise ValueError("Refill request not found")

        self.requests[request_id]["status"] = status

    def get_request(self, request_id):
        """
        Return a refill request by its ID.
        """
        if request_id not in self.requests:
            raise ValueError("Refill request not found")

        return self.requests[request_id]