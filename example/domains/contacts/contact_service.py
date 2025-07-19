"""Contact management service."""


class ContactService:
    """Service for managing contacts."""

    def __init__(self):
        self.contacts = []

    def add_contact(self, name, email):
        """Add a new contact."""
        contact = {"name": name, "email": email, "id": len(self.contacts) + 1}
        self.contacts.append(contact)
        return contact

    def get_contact(self, contact_id):
        """Get contact by ID."""
        for contact in self.contacts:
            if contact["id"] == contact_id:
                return contact
        return None

    def list_contacts(self):
        """List all contacts."""
        return self.contacts.copy()
