import logging

import ckan.lib.uploader as uploader
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import validate

from ckanext.showcase.logic.schema import showcase_package_association_create_schema
from ckanext.showcase.model import ShowcasePackageAssociation

log = logging.getLogger(__name__)


def showcase_create(context, data_dict):
    '''Upload the image and continue with package creation.'''

    upload = uploader.Upload('showcase')
    upload.update_data_dict(data_dict, 'image_url',
                            'image_upload', 'clear_upload')

    upload.upload(uploader.get_max_image_size())

    pkg = toolkit.get_action('package_create')(context, data_dict)

    return pkg


def showcase_package_association_create(context, data_dict):
    '''Create an association between a showcase and a package.

    :param showcase_id: the id of the showcase to associate
    :type showcase_id: string

    :param package_id: the id of the package to associate
    :type package_id: string
    '''

    toolkit.check_access('ckanext_showcase_package_association_create', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict, showcase_package_association_create_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, showcase_id = toolkit.get_or_bust(validated_data_dict, ['package_id', 'showcase_id'])

    if ShowcasePackageAssociation.exists(package_id=package_id, showcase_id=showcase_id):
        raise toolkit.ValidationError("ShowcasePackageAssociation with package_id '{0}' and showcase_id '{1}' already exists.".format(package_id, showcase_id))

    # create the association
    ShowcasePackageAssociation.create(package_id=package_id, showcase_id=showcase_id)

    return 'lol'
