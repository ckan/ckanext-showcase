import ckan.lib.base as base
from ckan.common import c
from ckan.controllers.user import UserController

render = base.render

import logging
log = logging.getLogger(__name__)


class ShowcaseDashboardController(UserController):

    def dashboard_showandtell(self):
        '''Display all Show & Tell items created by the user.'''
        context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        data_dict = {'user_obj': c.userobj}
        self._setup_template_variables(context, data_dict)
        return render('user/dashboard_showandtell.html')
