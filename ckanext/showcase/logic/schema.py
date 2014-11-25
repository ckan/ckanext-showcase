from ckan.logic.validators import package_id_or_name_exists

from ckan.lib.navl.validators import not_empty


def showcase_package_association_create_schema():

    schema = {
        'package_id': [not_empty, unicode, package_id_or_name_exists],
        'showcase_id': [not_empty, unicode, package_id_or_name_exists]
    }

    return schema
