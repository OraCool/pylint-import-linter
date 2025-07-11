"""Core document functionality."""

# Note: The following import would be flagged as a DDD violation - testing clean config
from example.domains.pd_common.core import BaseService, ValidationError

# from example.domains.billing.payments import PaymentService # This should be flagged


class Document:
    """Document entity."""

    def __init__(self, document_id, title, content, workspace_id):
        self.document_id = document_id
        self.title = title
        self.content = content
        self.workspace_id = workspace_id
        self.status = "draft"

    def publish(self):
        """Publish document."""
        self.status = "published"


class DocumentService(BaseService):
    """Core document service."""

    def create_document(self, title, content, workspace_id):
        """Create a new document."""
        if not title:
            raise ValidationError("Document title is required")

        document = Document(
            document_id=f"doc_{hash(title + workspace_id)}",
            title=title,
            content=content,
            workspace_id=workspace_id,
        )

        return document

    def get_document(self, document_id):
        """Retrieve document by ID."""
        # Mock implementation
        return Document(document_id, "Sample Doc", "Content", "ws_123")
