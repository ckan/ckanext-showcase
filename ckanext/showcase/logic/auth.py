import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckanext.showcase.model import ShowcaseAdmin

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
        'ckanext_showcase_admin_add': add_showcase_admin,
        'ckanext_showcase_admin_remove': remove_showcase_admin,
        'ckanext_showcase_admin_list': showcase_admin_list,
        'ckanext_showcase_upload': showcase_upload,
    }


def _is_showcase_admin(context):
    '''
    Determines whether user in context is in the showcase admin list.
    '''
    user = context.get('user', '')
    userobj = model.User.get(user)
    return ShowcaseAdmin.is_user_showcase_admin(userobj)


def create(context, data_dict):
    '''Create a Showcase.

       Only sysadmin or users listed as Showcase Admins can create a Showcase.
    '''
    return {'success': _is_showcase_admin(context)}


def delete(context, data_dict):
    '''Delete a Showcase.

       Only sysadmin or users listed as Showcase Admins can delete a Showcase.
    '''
    return {'success': _is_showcase_admin(context)}


def update(context, data_dict):
    '''Update a Showcase.

       Only sysadmin or users listed as Showcase Admins can update a Showcase.
    '''
    return {'success': _is_showcase_admin(context)}


@toolkit.auth_allow_anonymous_access
def show(context, data_dict):
    '''All users can access a showcase show'''
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def showcase_list(context, data_dict):
    '''All users can access a showcase list'''
    return {'success': True}


def package_association_create(context, data_dict):
    '''Create a package showcase association.

       Only sysadmins or user listed as Showcase Admins can create a
       package/showcase association.
    '''
    return {'success': _is_showcase_admin(context)}


def package_association_delete(context, data_dict):
    '''Delete a package showcase association.

       Only sysadmins or user listed as Showcase Admins can delete a
       package/showcase association.
    '''
    return {'success': _is_showcase_admin(context)}


@toolkit.auth_allow_anonymous_access
def showcase_package_list(context, data_dict):
    '''All users can access a showcase's package list'''
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def package_showcase_list(context, data_dict):
    '''All users can access a packages's showcase list'''
    return {'success': True}


def add_showcase_admin(context, data_dict):
    '''Only sysadmins can add users to showcase admin list.'''
    return {'success': False}


def remove_showcase_admin(context, data_dict):
    '''Only sysadmins can remove users from showcase admin list.'''
    return {'success': False}


def showcase_admin_list(context, data_dict):
    '''Only sysadmins can list showcase admin users.'''
    return {'success': False}

def showcase_upload(context, data_dict):
    '''Only sysadmins can upload images.'''
    return {'success': _is_showcase_admin(context)}
