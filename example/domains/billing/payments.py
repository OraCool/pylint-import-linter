"""Payment processing within billing domain."""

from domains.pd_common.clients import APIClient
from domains.pd_common.core import BaseService, ValidationError, format_currency


class Payment:
    """Payment entity."""

    def __init__(self, payment_id, amount, currency, workspace_id):
        self.payment_id = payment_id
        self.amount = amount
        self.currency = currency
        self.workspace_id = workspace_id
        self.status = "pending"

    def complete(self):
        """Mark payment as completed."""
        self.status = "completed"


class PaymentService(BaseService):
    """Service for payment processing."""

    def __init__(self):
        super().__init__()
        self.payment_gateway = APIClient("https://payment-api.com", "key")

    def process_payment(self, amount, currency, workspace_id):
        """Process a payment."""
        if amount <= 0:
            raise ValidationError("Payment amount must be positive")

        payment = Payment(
            payment_id=f"pay_{hash(f'{amount}{workspace_id}')}",
            amount=amount,
            currency=currency,
            workspace_id=workspace_id,
        )

        # Process with external gateway
        response = self.payment_gateway.make_request(
            "/charge", method="POST", data={"amount": amount, "currency": currency}
        )

        if response["status"] == "success":
            payment.complete()

        return payment

    def get_formatted_amount(self, payment):
        """Get formatted payment amount."""
        return format_currency(payment.amount, payment.currency)
