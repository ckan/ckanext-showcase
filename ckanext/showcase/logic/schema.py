import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.validators import not_empty

from ckanext.showcase.logic.validators import (convert_package_name_or_id_to_id_for_type_dataset,
                                               convert_package_name_or_id_to_id_for_type_showcase)


def showcase_base_schema():
    schema = {
        'image_url': [toolkit.get_validator('ignore_missing'),
                      toolkit.get_converter('convert_to_extras')]
    }
    return schema


def showcase_create_schema():
    return showcase_base_schema()


def showcase_update_schema():
    return showcase_base_schema()


def showcase_show_schema():
    schema = showcase_base_schema()
    schema.update({
        'image_url': [toolkit.get_converter('convert_from_extras'),
                      toolkit.get_validator('ignore_missing')]
    })
    return schema


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
