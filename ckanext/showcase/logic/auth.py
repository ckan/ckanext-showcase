import ckan.plugins.toolkit as tk
import ckan.model as model
from ckan.common import _
from ckanext.showcase import utils
from sqlalchemy import or_

from ckanext.showcase.model import ShowcaseApprovalStatus
from ckanext.showcase.data.constants import *
import ckan.authz as authz

import logging
log = logging.getLogger(__name__)


def get_auth_functions():
    return {
        'ckanext_showcase_create': create,
        'ckanext_showcase_update': update,
        'ckanext_showcase_delete': delete,
        'ckanext_showcase_show': show,
        'ckanext_showcase_list': showcase_list,
        'ckanext_showcase_package_association_create': package_association_create,
        'ckanext_showcase_package_association_delete': package_association_delete,
        'ckanext_showcase_package_list': showcase_package_list,
        'ckanext_package_showcase_list': package_showcase_list,
        'ckanext_showcase_upload': showcase_upload,

        # Approval Workflow
        'ckanext_showcase_status_show': status_show,
        'ckanext_showcase_status_update': status_update,
    }


def _is_user_the_creator(context, data_dict, key='id'):
    if authz.auth_is_anon_user(context): return False

    user = context.get('user')
    model = context['model']
    user_obj = model.User.get(user)

    q = model.Session.query(model.Package) \
        .filter(model.Package.type == utils.DATASET_TYPE_NAME)\
        .filter(model.Package.creator_user_id == user_obj.id)\
        .filter(or_(
            model.Package.id == data_dict.get(key,''),
            model.Package.name == data_dict.get(key,''),
            ))
    
    return bool(q.count())


def create(context, data_dict):
    return {'success': (not authz.auth_is_anon_user(context))}


def delete(context, data_dict):
    return {
        'success': False, 
        'msg': _('User not authorized to delete a submitted Reuse')
        }


def update(context, data_dict):
    if _is_user_the_creator(context, data_dict):
        return {'success': True}
    else:
        return {
            'success': False, 
            'msg': _('User not authorized to delete a submitted Reuse')
            }


@tk.auth_allow_anonymous_access
def show(context, data_dict):
    '''All users can access a showcase show'''
    showcase_id = data_dict.get('id','')

    showcase = model.Session.query(model.Package) \
        .filter(model.Package.id == showcase_id)\
        .filter(model.Package.type == utils.DATASET_TYPE_NAME)\
        .first()


    if not showcase:
        return {'success': False, 'msg': _('Reuse does not exist')}


    status_obj = ShowcaseApprovalStatus.get(showcase_id=showcase_id).as_dict() or ShowcaseApprovalStatus.update_status(showcase_id,'')

    if status_obj['status'] == ApprovalStatus.APPROVED.value \
                or _is_user_the_creator(context, data_dict) \
                or authz.is_authorized_boolean('is_portal_admin', context):
        return {'success': True}
    else:
        return {'success': False, 'msg': _('User not authorized to view this Reuse')}


@tk.auth_allow_anonymous_access
def showcase_list(context, data_dict):
    '''All users can access a showcase list'''
    return {'success': True}


def package_association_create(context, data_dict):
    '''Create a package showcase association.

       Only sysadmins or user listed as Showcase Admins can create a
       package/showcase association.
    '''
    return {'success': _is_user_the_creator(context, data_dict, 'showcase_id')}


def package_association_delete(context, data_dict):
    '''Delete a package showcase association.

       Only sysadmins or user listed as Showcase Admins can delete a
       package/showcase association.
    '''
    return {'success': _is_user_the_creator(context, data_dict, 'showcase_id')}


@tk.auth_allow_anonymous_access
def showcase_package_list(context, data_dict):
    '''All users can access a showcase's package list'''
    showcase_id = data_dict.get('showcase_id', None)
    return authz.is_authorized(
            'ckanext_showcase_show',
            context, {**data_dict, "id":showcase_id}
            )


@tk.auth_allow_anonymous_access
def package_showcase_list(context, data_dict):
    '''All users can access a packages's showcase list'''
    return {'success': True}


def showcase_upload(context, data_dict):
    return {'success': (not authz.auth_is_anon_user(context))}


def status_show(context, data_dict):
    showcase_id = data_dict.get('id','')
    showcase = tk.get_action('ckanext_showcase_show')(
        context, 
        {'id': data_dict['id']}
    )

    if not showcase:
        return {'success': False, 'msg': _('Reuse does not exist')}

    status_obj = ShowcaseApprovalStatus.get(showcase_id=showcase_id).as_dict() \
        or ShowcaseApprovalStatus.update_status(showcase_id,'')

    if status_obj['status'] == ApprovalStatus.APPROVED.value \
        or _is_user_the_creator(context, data_dict) \
        or authz.is_authorized_boolean('is_portal_admin', context):
        return {'success': True}
    else:
        return {'success': False, 'msg': _('User not authorized to view the status')}


def status_update(context, data_dict):
    if authz.is_authorized_boolean('is_portal_admin', context):
        return {'success': True}

    return {'success': False, 'msg': _('User not authorized to update Reuse status')}