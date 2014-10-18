import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
from ckan.common import c, request, _

from ckan.controllers.group import GroupController

render = base.render
abort = base.abort

NotAuthorized = logic.NotAuthorized

import logging
log = logging.getLogger(__name__)


class ShowcaseController(GroupController):
    group_type = 'showcase'

    def index(self):
        group_type = self._guess_group_type()

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')
        data_dict = {'all_fields': True, 'q': q}
        sort_by = c.sort_by_selected = request.params.get('sort')
        if sort_by:
            data_dict['sort'] = sort_by
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        # if c.userobj:
        #     context['user_id'] = c.userobj.id
        #     context['user_is_admin'] = c.userobj.sysadmin

        data_dict['type'] = group_type
        results = self._action('group_list')(context, data_dict)

        c.page = h.Page(
            collection=results,
            page=request.params.get('page', 1),
            url=h.pager_url,
            items_per_page=21
        )
        return render(self._index_template(group_type))
