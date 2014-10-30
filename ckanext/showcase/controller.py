import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
from ckan.common import c, request, _

from ckan.controllers.package import PackageController

render = base.render
abort = base.abort

NotAuthorized = logic.NotAuthorized

import logging
log = logging.getLogger(__name__)


class ShowcaseController(PackageController):
    pass
