"""Template management within document domain."""

from example.domains.pd_common.core import BaseService

from .documents_core import DocumentService


class Template:
    """Template entity."""

    def __init__(self, template_id, name, content):
        self.template_id = template_id
        self.name = name
        self.content = content
        self.variables = []


class TemplateService(BaseService):
    """Service for template management."""

    def __init__(self):
        super().__init__()
        self.document_service = DocumentService()  # OK: internal domain dependency

    def create_template(self, name, content):
        """Create a new template."""
        template = Template(template_id=f"tpl_{hash(name)}", name=name, content=content)
        return template

    def create_document_from_template(self, template_id, workspace_id, title=None):
        """Create document from template."""
        # Mock template retrieval
        template = Template(template_id, "Sample Template", "Template content")

        document_title = title or f"Document from {template.name}"

        # Use internal document service
        document = self.document_service.create_document(
            title=document_title, content=template.content, workspace_id=workspace_id
        )

        return document
