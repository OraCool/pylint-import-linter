"""External API clients and integrations."""


class APIClient:
    """Base API client."""

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def make_request(self, endpoint, method="GET", data=None):
        """Make HTTP request to external API."""
        # Mock implementation
        return {"status": "success", "data": data}


class EmailClient:
    """Email service client."""

    def send_email(self, to, subject, body):
        """Send email notification."""
        print(f"Sending email to {to}: {subject}")
        return True
