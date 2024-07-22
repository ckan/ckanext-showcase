from enum import Enum

class ApprovalStatus(Enum):
    PENDING = "Pending"
    NEEDS_REVISION = "Needs Revision"
    REJECTED = "Rejected"
    APPROVED = "Approved"