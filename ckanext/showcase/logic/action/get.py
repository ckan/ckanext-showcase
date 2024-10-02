import ckan.plugins.toolkit as tk
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.lib.navl.dictization_functions import validate
from ckan.logic import validate as validate_decorator
from ckanext.showcase import utils
from sqlalchemy import or_
from ckanext.showcase.data.constants import *
import ckan.authz as authz
import datetime
from ckanext.showcase.logic.schema import (showcase_package_list_schema,
                                           package_showcase_list_schema,
                                           showcase_search_schema)
from ckanext.showcase.model import ShowcasePackageAssociation, ShowcaseApprovalStatus
from sqlalchemy import Column, ForeignKey, types, or_, func
import ckan.lib.dictization.model_dictize as md


import logging
log = logging.getLogger(__name__)


@tk.side_effect_free
def showcase_show(context, data_dict):
    tk.check_access('ckanext_showcase_show', context, data_dict)

    pkg_dict = tk.get_action('package_show')(context, data_dict)
    
    approval_status = ShowcaseApprovalStatus.get_status_for_showcase(pkg_dict.get('id'))
    
    if approval_status:
        approval_status = approval_status.as_dict()
    else:
        approval_status = ShowcaseApprovalStatus.update_status(pkg_dict.get('id'))

    pkg_dict['approval_status'] = approval_status

    model = context["model"]
    user = context.get('user')
    user_obj = model.User.get(user)

    pkg_dict['creator'] = md.user_dictize(user_obj, context)
    return pkg_dict


@tk.side_effect_free
def showcase_list(context, data_dict):
    '''Return a list of all showcases in the site.'''

    tk.check_access('ckanext_showcase_list', context, data_dict)

    # model = context["model"]
    # user = context.get('user')
    # user_obj = model.User.get(user)

    offset = data_dict.pop('page', 1) - 1 
    limit = data_dict.pop('limit', 20)

    data_dict['status'] = ApprovalStatus.APPROVED.value
    q = ShowcaseApprovalStatus.filter_showcases(**data_dict)
    total = q.count() 

    if limit != -1:
        q = q.offset(offset * limit).limit(limit)
    
    showcase_ids_list = []
    for pkg in q.all():
        showcase_ids_list.append(
            pkg.id
        )

    return {
        'items': showcase_ids_list,
        'total': total
        }


@tk.side_effect_free
@validate_decorator(showcase_search_schema)
def showcase_filtered(context, data_dict):
    '''Return a list of all showcases in the site.'''
    tk.check_access('ckanext_showcase_list', context, data_dict)
    model = context["model"]
    user = context.get('user')
    user_obj = model.User.get(user)

    offset = data_dict.pop('page', 1) - 1 
    limit = data_dict.pop('limit', 20)


    if not authz.is_authorized_boolean('is_portal_admin', context):
        data_dict['creator_user_id'] = user_obj.id
    
    q = ShowcaseApprovalStatus.filter_showcases(**data_dict)

    total = q.count() 
    if limit != -1:
        q = q.offset(offset * limit).limit(limit)

    showcase_list = []
    for pkg in q.all():
        showcase_list.append(
            tk.get_action('ckanext_showcase_show')(context, {'id': pkg.id})
            )

    return {
        'items': showcase_list,
        'total': total
        }


@tk.side_effect_free
def showcase_package_list(context, data_dict):
    '''List packages associated with a showcase.

    :param showcase_id: id or name of the showcase
    :type showcase_id: string

    :rtype: list of dictionaries
    '''

    tk.check_access('ckanext_showcase_package_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           showcase_package_list_schema(),
                                           context)

    if errors:
        raise tk.ValidationError(errors)

    # get a list of package ids associated with showcase id
    pkg_id_list = ShowcasePackageAssociation.get_package_ids_for_showcase(
        validated_data_dict['showcase_id'])

    pkg_list = []
    if pkg_id_list:
        # for each package id, get the package dict and append to list if
        # active
        id_list = []
        for pkg_id in pkg_id_list:
            id_list.append(pkg_id[0])
        q = 'id:(' + ' OR '.join(['{0}'.format(x) for x in id_list]) + ')'
        _pkg_list = tk.get_action('package_search')(
            context,
            {'q': q, 'rows': 100})
        pkg_list = _pkg_list['results']
    return pkg_list


@tk.side_effect_free
def package_showcase_list(context, data_dict):
    '''List showcases associated with a package.

    :param package_id: id or name of the package
    :type package_id: string

    :rtype: list of dictionaries
    '''

    tk.check_access('ckanext_package_showcase_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           package_showcase_list_schema(),
                                           context)

    if errors:
        raise tk.ValidationError(errors)

    # get a list of showcase ids associated with the package id
    showcase_id_list = ShowcasePackageAssociation.get_showcase_ids_for_package(
        validated_data_dict['package_id']
        )
    showcase_list = []

    q = ''
    fq = ''
    if showcase_id_list:
        id_list = []
        for showcase_id in showcase_id_list:
            id_list.append(showcase_id[0])
        fq = 'dataset_type:showcase'
        q = 'id:(' + ' OR '.join(['{0}'.format(x) for x in id_list]) + ')'
        _showcase_list = tk.get_action('package_search')(
            context,
            {'q': q, 'fq': fq, 'rows': 100})
        showcase_list = _showcase_list['results']

    return showcase_list


@tk.side_effect_free
def status_show(context, data_dict):
    tk.check_access('ckanext_showcase_status_show', context, data_dict)

    showcase_id = data_dict.get('showcase_id', None)
    feedback_instance = ShowcaseApprovalStatus.get_status_for_showcase(showcase_id=showcase_id).as_dict()

    return feedback_instance



@tk.side_effect_free
def showcase_statics(context, data_dict):
    tk.check_access('ckanext_showcase_list', context, data_dict)

    model = context["model"]
    user = context.get('user')
    user_obj = model.User.get(user)
    
    if authz.is_authorized_boolean('is_portal_admin', context):
        return ShowcaseApprovalStatus.generate_statistics()
    else:
        return ShowcaseApprovalStatus.generate_statistics(
            creator_user_id=user_obj.id
        )