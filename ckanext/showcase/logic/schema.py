from ckan.logic.validators import package_id_or_name_exists
from ckan.logic.converters import convert_package_name_or_id_to_id

from ckan.lib.navl.validators import not_empty


def showcase_package_association_create_schema():
    schema = {
        'package_id': [not_empty, unicode, package_id_or_name_exists, convert_package_name_or_id_to_id],
        'showcase_id': [not_empty, unicode, package_id_or_name_exists, convert_package_name_or_id_to_id]
    }
    return schema


def showcase_package_list_schema():
    schema = {
        'showcase_id': [not_empty, unicode, package_id_or_name_exists, convert_package_name_or_id_to_id]
    }
    return schema
