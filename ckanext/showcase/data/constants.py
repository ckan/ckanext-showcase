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


class ReuseCaseType(Enum):
    MOBILE_APPLICATION = 'a'
    WEB_APPLICATION = 'b'
    ARCTICLE = 'c'
    SCIENTIFIC_RESEARCH = 'd'
    DEVELOPMENT_API = 'e'


REUSE_CASE_TYPE_OPTIONS = {
    'a': _(u"Mobile Application"),
    'b': _(u"Web Application"),
    'c': _(u"Writing a newspaper article, blog article, or research paper"),
    'd': _(u"Conducting scientific research or analysis"),
    'e':_(u"Development API"),
}
