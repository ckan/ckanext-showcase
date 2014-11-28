import ckan.plugins.toolkit as toolkit

import logging
log = logging.getLogger(__name__)


def create(context, data_dict):
    return {'success': False}


def package_association_create(context, data_dict):
    return {'success': False}


def update(context, data_dict):
    return {'success': False}


@toolkit.auth_allow_anonymous_access
def showcase_package_list(context, data_dict):
    '''All users can access a showcase's package list'''
    return {'success': True}
