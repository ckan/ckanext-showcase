import logging

import ckan.lib.uploader as uploader
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from ckan.logic.converters import convert_user_name_or_id_to_id
from ckan.lib.navl.dictization_functions import validate

import ckanext.showcase.logic.converters as showcase_converters
import ckanext.showcase.logic.schema as showcase_schema
from ckanext.showcase.model import ShowcasePackageAssociation, ShowcaseAdmin

convert_package_name_or_id_to_title_or_name = \
    showcase_converters.convert_package_name_or_id_to_title_or_name
showcase_package_association_create_schema = \
    showcase_schema.showcase_package_association_create_schema
showcase_admin_add_schema = showcase_schema.showcase_admin_add_schema

log = logging.getLogger(__name__)


def showcase_create(context, data_dict):
    '''Upload the image and continue with package creation.'''

    # force type to 'showcase'
    data_dict['type'] = 'showcase'
    upload = uploader.get_uploader('showcase')

    upload.update_data_dict(data_dict, 'image_url',
                            'image_upload', 'clear_upload')

    upload.upload(uploader.get_max_image_size())

    pkg = toolkit.get_action('package_create')(context, data_dict)

    return pkg


def showcase_package_association_create(context, data_dict):
    '''Create an association between a showcase and a package.

    :param showcase_id: id or name of the showcase to associate
    :type showcase_id: string

    :param package_id: id or name of the package to associate
    :type package_id: string
    '''

    toolkit.check_access('ckanext_showcase_package_association_create',
                         context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, showcase_package_association_create_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, showcase_id = toolkit.get_or_bust(validated_data_dict,
                                                  ['package_id',
                                                   'showcase_id'])

    if ShowcasePackageAssociation.exists(package_id=package_id,
                                         showcase_id=showcase_id):
        raise toolkit.ValidationError("ShowcasePackageAssociation with package_id '{0}' and showcase_id '{1}' already exists.".format(package_id, showcase_id),
                                      error_summary=u"The dataset, {0}, is already in the showcase".format(convert_package_name_or_id_to_title_or_name(package_id, context)))

    # create the association
    return ShowcasePackageAssociation.create(package_id=package_id,
                                             showcase_id=showcase_id)


def showcase_admin_add(context, data_dict):
    '''Add a user to the list of showcase admins.

    :param username: name of the user to add to showcase user admin list
    :type username: string
    '''

    toolkit.check_access('ckanext_showcase_admin_add', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, showcase_admin_add_schema(), context)

    username = toolkit.get_or_bust(validated_data_dict, 'username')
    try:
        user_id = convert_user_name_or_id_to_id(username, context)
    except toolkit.Invalid:
        raise toolkit.ObjectNotFound

    if errors:
        raise toolkit.ValidationError(errors)

    if ShowcaseAdmin.exists(user_id=user_id):
        raise toolkit.ValidationError("ShowcaseAdmin with user_id '{0}' already exists.".format(user_id),
                                      error_summary=u"User '{0}' is already a Showcase Admin.".format(username))

    # create showcase admin entry
    return ShowcaseAdmin.create(user_id=user_id)


def showcase_upload(context, data_dict):
    ''' Uploads images to be used in showcase content.

    '''
    toolkit.check_access('ckanext_showcase_upload', context, data_dict)

    upload = uploader.get_uploader('showcase_image')

    upload.update_data_dict(data_dict, 'image_url', 'upload', 'clear_upload')
    upload.upload(uploader.get_max_image_size())

    image_url = data_dict.get('image_url')
    if image_url and image_url[0:6] not in {'http:/', 'https:'}:
        image_url = h.url_for_static(
           'uploads/showcase_image/{}'.format(image_url),
            qualified=True
        )
    return {'url': image_url}
