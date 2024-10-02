from enum import Enum
from ckan.plugins.toolkit import _

class ApprovalStatus(Enum):
    PENDING = 'a'
    NEEDS_REVISION = 'b'
    REJECTED = 'c'
    APPROVED = 'd'


SHOWCASE_STATUS_OPTIONS = {
    'a' : _(u"Pending"),
    'b': _(u"Needs Revision"),
    'c': _(u"Rejected"),
    'd': _(u"Approved"),
}