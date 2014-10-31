import logging
log = logging.getLogger(__name__)


def create(context, data_dict):
    return {'success': False, 'msg': 'Only Site Admins can create Showcases'}


def update(context, data_dict):
    return {'success': False, 'msg': 'Only Site Admins can update Showcases'}
