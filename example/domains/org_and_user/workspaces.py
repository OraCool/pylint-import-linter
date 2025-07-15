"""Workspace management within org_and_user domain."""

from domains.pd_common.core import BaseService, ValidationError

from .users import UserService


class Workspace:
    """Workspace entity."""

    def __init__(self, workspace_id, name, owner_id):
        self.workspace_id = workspace_id
        self.name = name
        self.owner_id = owner_id
        self.members = []

    def add_member(self, user_id):
        """Add member to workspace."""
        if user_id not in self.members:
            self.members.append(user_id)


class WorkspaceService(BaseService):
    """Service for workspace management operations."""

    def __init__(self):
        super().__init__()
        self.user_service = UserService()  # OK: internal domain dependency

    def create_workspace(self, name, owner_email):
        """Create a new workspace."""
        if not name:
            raise ValidationError("Workspace name is required")

        # Get owner user
        owner = self.user_service.get_user_by_email(owner_email)

        workspace = Workspace(
            workspace_id=f"ws_{hash(name + owner_email)}",
            name=name,
            owner_id=owner.user_id,
        )

        return workspace

    def add_member_to_workspace(self, workspace_id, user_email):
        """Add member to workspace."""
        user = self.user_service.get_user_by_email(user_email)
        # Mock workspace retrieval and member addition
        print(f"Adding user {user.email} to workspace {workspace_id}")
        return True
