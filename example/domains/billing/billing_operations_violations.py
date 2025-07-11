"""Billing operations that violate DDD boundaries (for testing)."""

# VIOLATION: Billing domain accessing org_and_user internals directly
from domains.org_and_user.users import UserService  # This should be flagged
from domains.pd_common.core import BaseService

from .payments import PaymentService


class BillingOperationsService(BaseService):
    """Service that demonstrates billing boundary violations."""

    def __init__(self):
        super().__init__()
        self.payment_service = PaymentService()

        # This should be flagged as a violation
        self.user_service = UserService()  # VIOLATION

    def charge_user_directly(self, user_email, amount):
        """Charge user directly - violates boundaries."""

        # Direct access to user domain (violation)
        user = self.user_service.get_user_by_email(user_email)

        # Process payment
        payment = self.payment_service.process_payment(
            amount=amount,
            currency="USD",
            workspace_id="default",  # This is wrong architecture
        )

        return {"user": user, "payment": payment}
