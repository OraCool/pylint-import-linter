"""Valid cross-domain integration through proper interfaces."""

from domains.org_and_user.users import UserService
from domains.org_and_user.workspaces import WorkspaceService
from domains.pd_common.core import BaseService


class OrganizationService(BaseService):
    """Service that properly manages organization-level operations."""

    def __init__(self):
        super().__init__()
        self.user_service = UserService()  # OK: internal domain
        self.workspace_service = WorkspaceService()  # OK: internal domain

    def setup_organization(self, admin_email, org_name):
        """Setup a new organization with admin user and workspace."""

        # Create admin user
        admin_user = self.user_service.create_user(email=admin_email, name="Admin User")

        # Create organization workspace
        workspace = self.workspace_service.create_workspace(name=org_name, owner_email=admin_email)

        return {"admin": admin_user, "workspace": workspace}

    def invite_user_to_organization(self, workspace_id, user_email, inviter_email):
        """Invite user to organization workspace."""

        # Verify inviter exists
        inviter = self.user_service.get_user_by_email(inviter_email)

        # Create or get invited user
        invited_user = self.user_service.get_user_by_email(user_email)

        # Add to workspace
        result = self.workspace_service.add_member_to_workspace(
            workspace_id=workspace_id, user_email=user_email
        )

        return {"inviter": inviter, "invited_user": invited_user, "success": result}
