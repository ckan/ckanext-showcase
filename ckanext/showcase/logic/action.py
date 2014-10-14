import ckan.new_authz as new_authz
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.plugins.toolkit as toolkit

import logging
log = logging.getLogger(__name__)


def showings_list_admin(context, data_dict):
    '''
    Return a list of showings groups for which the authorized user is admin.

    This is like login.action.get.group_list_authz, but without being tied up
    with 'organizations' conditionals.
    '''
    model = context['model']
    user = context['user']

    toolkit.check_access('group_list_authz', context, data_dict)

    if new_authz.auth_is_loggedin_user():
        user_id = new_authz.get_user_id_for_username(user, allow_none=True)
    else:
        return []

    if user_id is None:
        return []

    q = model.Session.query(model.Member) \
        .filter(model.Member.table_name == 'user') \
        .filter(model.Member.capacity == 'admin') \
        .filter(model.Member.table_id == user_id)
    group_ids = [row.group_id for row in q.all()]

    if not group_ids:
        return []

    q = model.Session.query(model.Group) \
        .filter(model.Group.type == 'showing') \
        .filter(model.Group.state == 'active')

    groups = q.filter(model.Group.id.in_(group_ids)).all()

    group_list = model_dictize.group_list_dictize(groups, context)
    return group_list
