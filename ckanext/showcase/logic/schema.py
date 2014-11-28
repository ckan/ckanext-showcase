from ckan.lib.navl.validators import not_empty

from ckanext.showcase.logic.validators import (convert_package_name_or_id_to_id_for_type_dataset,
                                               convert_package_name_or_id_to_id_for_type_showcase)


def showcase_package_association_create_schema():
    schema = {
        'package_id': [not_empty, unicode, convert_package_name_or_id_to_id_for_type_dataset],
        'showcase_id': [not_empty, unicode, convert_package_name_or_id_to_id_for_type_showcase]
    }
    return schema


def showcase_package_list_schema():
    schema = {
        'showcase_id': [not_empty, unicode, convert_package_name_or_id_to_id_for_type_showcase]
    }
    return schema


def package_showcase_list_schema():
    schema = {
        'package_id': [not_empty, unicode, convert_package_name_or_id_to_id_for_type_dataset]
    }
    return schema
