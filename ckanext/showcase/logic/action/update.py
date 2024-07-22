import logging

import ckan.lib.uploader as uploader
import ckan.plugins.toolkit as toolkit
from ckan.plugins import toolkit as tk
from ckanext.showcase.model import ShowcaseApprovalStatus
from ckan.common import _
import ckan.model as model
from ckan.lib.navl.dictization_functions import validate
from ckanext.showcase import utils
import ckanext.showcase.logic.schema as showcase_schema
from ckanext.showcase.data.constants import *

log = logging.getLogger(__name__)


def showcase_update(context, data_dict):
    toolkit.check_access('ckanext_showcase_update',context, data_dict)

    upload = uploader.get_uploader('showcase', data_dict['image_url'])

    upload.update_data_dict(data_dict, 'image_url',
                            'image_upload', 'clear_upload')

    upload.upload(uploader.get_max_image_size())

    site_user = toolkit.get_action("get_site_user")({"ignore_auth": True}, {})
    updated_context = {'ignore_auth': True, 'user':site_user['name']}
    pkg = toolkit.get_action('package_update')(
        context.update(updated_context), 
        data_dict
        )

    toolkit.get_action('ckanext_showcase_status_update')(
        context.update(updated_context),
        {"showcase_id": pkg.get("id",pkg.get("name", '')) }
    )

    return pkg


def status_update(context, data_dict):
    toolkit.check_access('ckanext_showcase_status_update',context, data_dict)
    
    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, showcase_schema.showcase_status_update_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)
    
    showcase_id = validated_data_dict.get('showcase_id')
    feedback = validated_data_dict.get('feedback','')
    status = validated_data_dict.get('status', ApprovalStatus.PENDING)

    q = model.Session.query(model.Package.id)\
        .filter(
            model.Package.id == showcase_id, 
            model.Package.type == utils.DATASET_TYPE_NAME
            )

    if not q:
        tk.abort(404, _('Showcase not found.\n Inavlid showcase_id.'))

    update_status = ShowcaseApprovalStatus.update_status(
        showcase_id,
        feedback,
        status
    )

    return update_status


