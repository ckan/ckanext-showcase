from ckan.plugins import toolkit as tk
from ckanext.showcase.data.constants import *
_ = tk._
Invalid = tk.Invalid
import datetime

def convert_package_name_or_id_to_id_for_type(package_name_or_id,
                                              context, package_type='dataset'):
    '''
    Return the id for the given package name or id. Only works with packages
    of type package_type.

    Also validates that a package with the given name or id exists.

    :returns: the id of the package with the given name or id
    :rtype: string
    :raises: ckan.lib.navl.dictization_functions.Invalid if there is no
        package with the given name or id

    '''
    session = context['session']
    model = context['model']
    result = session.query(model.Package) \
        .filter_by(id=package_name_or_id, type=package_type).first()
    if not result:
        result = session.query(model.Package) \
            .filter_by(name=package_name_or_id, type=package_type).first()
    if not result:
        raise Invalid('%s: %s' % (_('Not found'), _('Dataset')))
    return result.id


def convert_package_name_or_id_to_id_for_type_dataset(package_name_or_id,
                                                      context):
    return convert_package_name_or_id_to_id_for_type(package_name_or_id,
                                                     context,
                                                     package_type='dataset')


def convert_package_name_or_id_to_id_for_type_showcase(package_name_or_id,
                                                       context):
    return convert_package_name_or_id_to_id_for_type(package_name_or_id,
                                                     context,
                                                     package_type='showcase')


def is_valid_status(applied_status, context):
    status_map = {status.value: status.name for status in ApprovalStatus}
    if applied_status not in status_map:
        raise Invalid(_(f"Invalid status: {applied_status}. Must be one of: {list(status_map.keys())}"))
    
    return ApprovalStatus[status_map[applied_status]]

def is_valid_filter_status(applied_status, context):
    status_map = {status.value: status.name for status in ApprovalStatus}
    if applied_status not in status_map:
        raise Invalid(_(f"Invalid status: {applied_status}. Must be one of: {list(status_map.keys())}"))
    
    return applied_status


def validate_status_feedback(key, flattened_data, errors, context):
    key1 = ('feedback',)
    feedback = flattened_data.get(key1)
    status = flattened_data.get(('status',))


    if status == ApprovalStatus.NEEDS_REVISION and not feedback:
        errors.get(key1, []).append(
            _("Feedback must be provided with the selected status")
        )
    else:
        flattened_data[key1] = feedback or '' 


def validate_reuse_types(applied_types, context):
    if isinstance(applied_types, str):
        applied_types = [applied_types]

    if not isinstance(applied_types, list):
        raise Invalid(_("Invalid input: Reuse types must be a list"))

    status_map = {status.value: status.name for status in ReuseCaseType}
    selected_types = []
    for c_type in applied_types:
        if c_type in status_map:
            selected_types.append(c_type)
        else:
            raise Invalid(_(f"Invalid type: {c_type}. Must be one of: {list(status_map.keys())}"))
    
    return selected_types

