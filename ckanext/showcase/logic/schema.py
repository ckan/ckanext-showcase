# -*- coding: utf-8 -*-
import ckan.plugins.toolkit as tk

from ckan.logic.schema import (default_tags_schema,
                               default_extras_schema,
                               default_resource_schema)

from ckanext.showcase.logic.validators import (
    convert_package_name_or_id_to_id_for_type_dataset,
    convert_package_name_or_id_to_id_for_type_showcase,
    is_valid_filter_status,
    is_valid_status,
    validate_reuse_types,
    validate_status_feedback
    )

if tk.check_ckan_version("2.10"):
    unicode_safe = tk.get_validator("unicode_safe")
else:
    unicode_safe = str

not_empty = tk.get_validator("not_empty")
empty = tk.get_validator("empty")
if_empty_same_as = tk.get_validator("if_empty_same_as")
ignore_missing = tk.get_validator("ignore_missing")
ignore = tk.get_validator("ignore")
keep_extras = tk.get_validator("keep_extras")

package_id_not_changed = tk.get_validator("package_id_not_changed")
name_validator = tk.get_validator("name_validator")
user_id_or_name_exists = tk.get_validator("user_id_or_name_exists")
package_name_validator = tk.get_validator("package_name_validator")
tag_string_convert = tk.get_validator("tag_string_convert")
ignore_not_package_admin = tk.get_validator("ignore_not_package_admin")
url_validator = tk.get_validator("url_validator")
convert_to_extras = tk.get_validator("convert_to_extras")
convert_from_extras = tk.get_validator("convert_from_extras")
ignore_empty = tk.get_validator("ignore_empty")
isodate = tk.get_validator("isodate")
natural_number_validator = tk.get_validator("natural_number_validator")
int_validator = tk.get_validator("int_validator")




def showcase_base_schema():
    schema = {
        'id': [empty],
        'revision_id': [ignore],
        'name': [not_empty, name_validator, package_name_validator],
        'title': [not_empty, unicode_safe],
        'title_ar': [convert_to_extras, not_empty, unicode_safe],
        'author': [ignore_missing, unicode_safe],
        'author_email': [ignore_missing, unicode_safe],
        'notes': [not_empty, unicode_safe],
        'notes_ar': [convert_to_extras, not_empty, unicode_safe],
        'reuse_type': [convert_to_extras, not_empty, validate_reuse_types],
        'url': [ignore_missing, url_validator],
        'state': [ignore_not_package_admin, ignore_missing],
        'type': [ignore_missing, unicode_safe],
        '__extras': [ignore],
        '__junk': [empty],
        'resources': default_resource_schema(),
        'tags': default_tags_schema(),
        'tag_string': [ignore_missing, tag_string_convert],
        'extras': default_extras_schema(),
        'save': [ignore],
        'return_to': [ignore],
        'image_url': [tk.get_validator('ignore_missing'),
                      tk.get_converter('convert_to_extras')]
    }
    return schema


def showcase_create_schema():
    return showcase_base_schema()


def showcase_update_schema():
    schema = showcase_base_schema()

    # Users can (optionally) supply the package id when updating a package, but
    # only to identify the package to be updated, they cannot change the id.
    schema['id'] = [ignore_missing, package_id_not_changed]

    # Supplying the package name when updating a package is optional (you can
    # supply the id to identify the package instead).
    schema['name'] = [ignore_missing, name_validator,
                      package_name_validator, unicode_safe]

    # Supplying the package title when updating a package is optional, if it's
    # not supplied the title will not be changed.
    schema['title'] = [ignore_missing, unicode_safe]

    return schema


def showcase_show_schema():
    schema = showcase_base_schema()
    # Don't strip ids from package dicts when validating them.
    schema['id'] = []

    schema.update({
        'tags': {'__extras': [keep_extras]}})

    schema.update({
        'state': [ignore_missing],
        'title_ar': [convert_from_extras, ignore_missing, unicode_safe],
        'notes_ar': [convert_from_extras, ignore_missing, unicode_safe],
        'reuse_type': [convert_from_extras, ignore_missing, unicode_safe],
        })

    # Remove validators for several keys from the schema so validation doesn't
    # strip the keys from the package dicts if the values are 'missing' (i.e.
    # None).
    schema['author'] = []
    schema['author_email'] = []
    schema['notes'] = []
    schema['url'] = []

    # Add several keys that are missing from default_create_package_schema(),
    # so validation doesn't strip the keys from the package dicts.
    schema['metadata_created'] = []
    schema['metadata_modified'] = []
    schema['creator_user_id'] = []
    schema['num_tags'] = []
    schema['revision_id'] = [ignore_missing]
    schema['tracking_summary'] = [ignore_missing]

    schema.update({
        'image_url': [tk.get_converter('convert_from_extras'),
                      tk.get_validator('ignore_missing')],
        'original_related_item_id': [
            tk.get_converter('convert_from_extras'),
            tk.get_validator('ignore_missing')]
    })

    return schema


def showcase_package_association_create_schema():
    schema = {
        'package_id': [not_empty, unicode_safe,
                       convert_package_name_or_id_to_id_for_type_dataset],
        'showcase_id': [not_empty, unicode_safe,
                        convert_package_name_or_id_to_id_for_type_showcase]
    }
    return schema


def showcase_package_association_delete_schema():
    return showcase_package_association_create_schema()


def showcase_package_list_schema():
    schema = {
        'showcase_id': [not_empty, unicode_safe,
                        convert_package_name_or_id_to_id_for_type_showcase]
    }
    return schema


def package_showcase_list_schema():
    schema = {
        'package_id': [not_empty, unicode_safe,
                       convert_package_name_or_id_to_id_for_type_dataset]
    }
    return schema



def showcase_status_update_schema():
    schema = {
        'showcase_id': [
            not_empty, 
            unicode_safe,
            convert_package_name_or_id_to_id_for_type_showcase
        ],
        "status": [
            ignore_missing,
            is_valid_status
        ],
        "feedback": [ignore_missing, unicode_safe],
        '__after': [validate_status_feedback],
    }
    return schema

def showcase_search_schema():
    schema = {
        'q':[ignore_missing, unicode_safe],
        "created_start": [ignore_missing, isodate],
        "created_end": [ignore_missing, isodate],
        'status': [ignore_empty, is_valid_filter_status],
        'page': [ignore_empty, natural_number_validator],
        'limit': [ignore_empty, int_validator],
        'sort': [ignore_missing, unicode_safe],
    }

    return schema