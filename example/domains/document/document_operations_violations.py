"""Document operations that violate DDD boundaries (for testing)."""

# VIOLATION: Document domain accessing billing internals directly
from domains.billing.payments import PaymentService  # This should be flagged

# VIOLATION: Document domain accessing org_and_user internals directly
from domains.org_and_user.users import UserService  # This should be flagged
from domains.org_and_user.workspaces import (  # This should be flagged
    WorkspaceService,
)
from domains.pd_common.core import BaseService

from .documents_core import DocumentService

# from org_and_user.org_admin import OrgAdminService  # Unused import removed


class DocumentOperationsService(BaseService):
    """Service that demonstrates boundary violations."""

    def __init__(self):
        super().__init__()
        self.document_service = DocumentService()

        # These should be flagged as violations
        self.user_service = UserService()  # VIOLATION
        self.workspace_service = WorkspaceService()  # VIOLATION
        self.payment_service = PaymentService()  # VIOLATION

    def create_paid_document(self, title, content, user_email, amount):
        """Create document with payment - violates boundaries."""

        # Direct access to user domain (violation)
        user = self.user_service.get_user_by_email(user_email)

        # Direct access to workspace domain (violation)
        workspace = self.workspace_service.create_workspace(
            name=f"{user.name}'s Workspace", owner_email=user_email
        )

        # Create document
        document = self.document_service.create_document(
            title=title, content=content, workspace_id=workspace.workspace_id
        )

        # Direct access to billing domain (violation)
        payment = self.payment_service.process_payment(
            amount=amount, currency="USD", workspace_id=workspace.workspace_id
        )

        return {"document": document, "payment": payment, "user": user}
