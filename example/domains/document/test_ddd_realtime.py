"""Test file to demonstrate real-time DDD violation detection."""

from example.domains.pd_common.core import BaseService  # This is OK - shared utilities

# Try adding the following imports one by one to see real-time highlighting:

# from example.domains.billing.payments import PaymentService  # ERROR
# from example.domains.org_and_user.users import UserService  # ERROR


class TestDocumentService(BaseService):
    """Test service to demonstrate DDD boundaries."""

    def test_method(self):
        """Test method."""
        return "DDD boundaries enforced"
