import logging

import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import validate

from ckanext.showcase.logic.schema import showcase_package_association_delete_schema
from ckanext.showcase.model import ShowcasePackageAssociation

log = logging.getLogger(__name__)


def showcase_package_association_delete(context, data_dict):
    '''Delete an association between a showcase and a package.

    :param showcase_id: id or name of the showcase in the association
    :type showcase_id: string

    :param package_id: id or name of the package in the association
    :type package_id: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_showcase_package_association_delete', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict, showcase_package_association_delete_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, showcase_id = toolkit.get_or_bust(validated_data_dict, ['package_id', 'showcase_id'])

    showcase_package_association = ShowcasePackageAssociation.get(package_id=package_id,
                                                                  showcase_id=showcase_id)

    if showcase_package_association is None:
        raise toolkit.ValidationError("ShowcasePackageAssociation with package_id '{0}' and showcase_id '{1}' doesn't exist.".format(package_id, showcase_id))

    # delete the association
    showcase_package_association.delete()
    model.repo.commit()
