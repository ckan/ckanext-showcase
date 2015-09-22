import logging

import ckan.plugins.toolkit as toolkit
from ckan.logic.converters import convert_user_name_or_id_to_id
import ckan.lib.navl.dictization_functions

from ckanext.showcase.logic.schema import (
    showcase_package_association_delete_schema,
    showcase_admin_remove_schema)

from ckanext.showcase.model import ShowcasePackageAssociation, ShowcaseAdmin

validate = ckan.lib.navl.dictization_functions.validate

log = logging.getLogger(__name__)


def showcase_delete(context, data_dict):
    '''Delete a showcase. Showcase delete cascades to
    ShowcasePackageAssociation objects.

    :param id: the id or name of the showcase to delete
    :type id: string
    '''

    model = context['model']
    id = toolkit.get_or_bust(data_dict, 'id')

    entity = model.Package.get(id)

    if entity is None:
        raise toolkit.ObjectNotFound

    toolkit.check_access('ckanext_showcase_delete', context, data_dict)

    entity.purge()
    model.repo.commit()


def showcase_package_association_delete(context, data_dict):
    '''Delete an association between a showcase and a package.

    :param showcase_id: id or name of the showcase in the association
    :type showcase_id: string

    :param package_id: id or name of the package in the association
    :type package_id: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_showcase_package_association_delete',
                         context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, showcase_package_association_delete_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, showcase_id = toolkit.get_or_bust(validated_data_dict,
                                                  ['package_id',
                                                   'showcase_id'])

    showcase_package_association = ShowcasePackageAssociation.get(
        package_id=package_id, showcase_id=showcase_id)

    if showcase_package_association is None:
        raise toolkit.ObjectNotFound("ShowcasePackageAssociation with package_id '{0}' and showcase_id '{1}' doesn't exist.".format(package_id, showcase_id))

    # delete the association
    showcase_package_association.delete()
    model.repo.commit()


def showcase_admin_remove(context, data_dict):
    '''Remove a user to the list of showcase admins.

    :param username: name of the user to remove from showcase user admin list
    :type username: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_showcase_admin_remove', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           showcase_admin_remove_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    username = toolkit.get_or_bust(validated_data_dict, 'username')
    user_id = convert_user_name_or_id_to_id(username, context)

    showcase_admin_to_remove = ShowcaseAdmin.get(user_id=user_id)

    if showcase_admin_to_remove is None:
        raise toolkit.ObjectNotFound("ShowcaseAdmin with user_id '{0}' doesn't exist.".format(user_id))

    showcase_admin_to_remove.delete()
    model.repo.commit()
