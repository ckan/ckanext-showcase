import logging
log = logging.getLogger(__name__)


def create(context, data_dict):
    return {'success': False, 'msg': 'Only Site Admins can create Showcases'}


def package_association_create(context, data_dict):
    return {'success': False, 'msg': 'Only Site Admins can associate Showcases with Packages'}


def update(context, data_dict):
    return {'success': False, 'msg': 'Only Site Admins can update Showcases'}
