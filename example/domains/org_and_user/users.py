"""User management within org_and_user domain."""

from example.domains.pd_common.clients import EmailClient
from example.domains.pd_common.core import BaseService, ValidationError


class User:
    """User entity."""

    def __init__(self, user_id, email, name):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.is_active = True

    def deactivate(self):
        """Deactivate user account."""
        self.is_active = False


class UserService(BaseService):
    """Service for user management operations."""

    def __init__(self):
        super().__init__()
        self.email_client = EmailClient()

    def create_user(self, email, name):
        """Create a new user."""
        if not email or "@" not in email:
            raise ValidationError("Invalid email address")

        user = User(user_id=f"user_{hash(email)}", email=email, name=name)

        self.email_client.send_email(
            to=email, subject="Welcome!", body=f"Welcome {name}!"
        )

        return user

    def get_user_by_email(self, email):
        """Retrieve user by email."""
        # Mock implementation
        return User(f"user_{hash(email)}", email, "John Doe")
