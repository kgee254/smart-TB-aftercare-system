from app.refills import RefillManager


class RefillService:
    """
    Service layer for refill operations.

    This class coordinates refill-related operations between
    the application and the RefillManager domain object.
    """

    def __init__(self, refill_manager):
        if not isinstance(refill_manager, RefillManager):
            raise TypeError(
                "refill_manager must be a RefillManager"
            )

        self.refill_manager = refill_manager

    def calculate_remaining_supply(self, doses_taken):
        """
        Calculate the patient's remaining medication supply.
        """
        return self.refill_manager.calculate_remaining_quantity(
            doses_taken
        )

    def check_supply(self, remaining_quantity, threshold):
        """
        Check whether medication supply is below the threshold.
        """
        return self.refill_manager.is_supply_low(
            remaining_quantity,
            threshold
        )

    def create_low_supply_alert(
        self,
        remaining_quantity,
        threshold
    ):
        """
        Create an alert when medication supply is low.
        """
        return self.refill_manager.create_alert(
            remaining_quantity,
            threshold
        )

    def request_refill(self):
        """
        Submit a refill request.
        """
        return self.refill_manager.request_refill()

    def update_request_status(self, request_id, status):
        """
        Update a refill request's status.
        """
        self.refill_manager.update_request_status(
            request_id,
            status
        )

    def get_request(self, request_id):
        """
        Retrieve a refill request.
        """
        return self.refill_manager.get_request(request_id)