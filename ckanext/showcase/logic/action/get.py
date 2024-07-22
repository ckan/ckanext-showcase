import ckan.plugins.toolkit as toolkit
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.lib.navl.dictization_functions import validate
from ckanext.showcase import utils
from sqlalchemy import or_
from ckanext.showcase.data.constants import *

from ckanext.showcase.logic.schema import (showcase_package_list_schema,
                                           package_showcase_list_schema)
from ckanext.showcase.model import ShowcasePackageAssociation, ShowcaseApprovalStatus

import logging
log = logging.getLogger(__name__)


@toolkit.side_effect_free
def showcase_show(context, data_dict):
    '''Return the pkg_dict for a showcase (package).

    :param id: the id or name of the showcase
    :type id: string
    '''

    toolkit.check_access('ckanext_showcase_show', context, data_dict)

    pkg_dict = toolkit.get_action('package_show')(context, data_dict)
    return pkg_dict


@toolkit.side_effect_free
def showcase_list(context, data_dict):
    '''Return a list of all showcases in the site.'''

    toolkit.check_access('ckanext_showcase_list', context, data_dict)

    model = context["model"]
    user = context.get('user')
    user_obj = model.User.get(user)

    offset = data_dict.get('offset', 0)
    limit = data_dict.get('limit', 20)

    q = model.Session.query(model.Package) \
        .filter(model.Package.type == utils.DATASET_TYPE_NAME) \
        .filter(model.Package.state == 'active')\
        .join(ShowcaseApprovalStatus, model.Package.id == ShowcaseApprovalStatus.showcase_id)

    if toolkit.get_action('is_portal_admin')(context, data_dict) or user_obj.sysadmin:
        pass
        # q = q.filter(ShowcaseApprovalStatus.status != ApprovalStatus.REJECTED)
    else:
        q = q.filter(or_(
                ShowcaseApprovalStatus.status == ApprovalStatus.APPROVED,
                model.Package.creator_user_id == user_obj.id
            ))

    if limit != -1: 
        q = q.offset(offset).limit(limit)
    
    showcase_list = []
    for pkg in q.all():
        showcase_list.append(model_dictize.package_dictize(pkg, context))

    return showcase_list

@toolkit.side_effect_free
def showcase_filtered(context, data_dict):
    '''Return a list of all showcases in the site.'''
    toolkit.check_access('ckanext_showcase_list', context, data_dict)
    model = context["model"]
    user = context.get('user')
    user_obj = model.User.get(user)

    offset = data_dict.get('offset', 0)
    limit = data_dict.get('limit', 20)

    status = data_dict.get('status', None)
    q = model.Session.query(model.Package) \
        .filter(model.Package.type == utils.DATASET_TYPE_NAME) \
        .filter(model.Package.state == 'active')\
        .join(ShowcaseApprovalStatus, model.Package.id == ShowcaseApprovalStatus.showcase_id)

    if not (toolkit.get_action('is_portal_admin')(context, data_dict) and user_obj.sysadmin):
        q = q.filter(or_(
                ShowcaseApprovalStatus.status == ApprovalStatus.APPROVED,
                model.Package.creator_user_id == user_obj.id
            ))

    if status:
        q = q.filter(ShowcaseApprovalStatus.status == status)

    if limit != -1:
        q = q.offset(offset).limit(limit)

    showcase_list = []
    for pkg in q.all():
        showcase_list.append(model_dictize.package_dictize(pkg, context))

    return showcase_list


@toolkit.side_effect_free
def showcase_package_list(context, data_dict):
    '''List packages associated with a showcase.

    :param showcase_id: id or name of the showcase
    :type showcase_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_showcase_package_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           showcase_package_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

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
        _pkg_list = toolkit.get_action('package_search')(
            context,
            {'q': q, 'rows': 100})
        pkg_list = _pkg_list['results']
    return pkg_list


@toolkit.side_effect_free
def package_showcase_list(context, data_dict):
    '''List showcases associated with a package.

    :param package_id: id or name of the package
    :type package_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_package_showcase_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           package_showcase_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

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
        _showcase_list = toolkit.get_action('package_search')(
            context,
            {'q': q, 'fq': fq, 'rows': 100})
        showcase_list = _showcase_list['results']

    return showcase_list

@toolkit.side_effect_free
def status_show(context, data_dict):
    toolkit.check_access('ckanext_showcase_status_show', context, data_dict)

    showcase_id = data_dict.get('showcase_id', None)
    feedback_instance = ShowcaseApprovalStatus.get(showcase_id=showcase_id)

    return feedback_instance