from enum import Enum
from ckan.plugins.toolkit import _

class ApprovalStatus(Enum):
    PENDING = _("Pending")
    NEEDS_REVISION = _("Needs Revision")
    REJECTED = _("Rejected")
    APPROVED = _("Approved")