# -*- coding: utf-8 -*-

from __future__ import print_function
import json
import logging

from collections import OrderedDict
import six
from six.moves.urllib.parse import urlencode

import ckan.model as model
import ckan.plugins as p
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
from ckanext.showcase.model import ShowcasePackageAssociation

_ = tk._
abort = tk.abort

log = logging.getLogger(__name__)
DATASET_TYPE_NAME = 'showcase'
ckan_29_or_higher = tk.check_ckan_version(min_version='2.9.0')


def check_edit_view_auth(id):
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'auth_user_obj': tk.g.userobj,
        'save': 'save' in tk.request.params,
        'pending': True
    }

    try:
        tk.check_access('ckanext_showcase_update', context)
    except tk.NotAuthorized:
        return tk.abort(
            401,
            _('User not authorized to edit {showcase_id}').format(
                showcase_id=id))


def check_new_view_auth():
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'auth_user_obj': tk.g.userobj,
        'save': 'save' in tk.request.params
    }

    # Check access here, then continue with PackageController.new()
    # PackageController.new will also check access for package_create.
    # This is okay for now, while only sysadmins can create Showcases, but
    # may not work if we allow other users to create Showcases, who don't
    # have access to create dataset package types. Same for edit below.
    try:
        tk.check_access('ckanext_showcase_create', context)
    except tk.NotAuthorized:
        return tk.abort(401, _('Unauthorized to create a package'))


def read_view(id):
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'for_view': True,
        'auth_user_obj': tk.g.userobj
    }
    data_dict = {'id': id}

    # check if showcase exists
    try:
        tk.g.pkg_dict = tk.get_action('package_show')(context, data_dict)
    except tk.ObjectNotFound:
        return tk.abort(404, _('Showcase not found'))
    except tk.NotAuthorized:
        return tk.abort(401, _('Unauthorized to read showcase'))

    # get showcase packages
    tk.g.showcase_pkgs = tk.get_action('ckanext_showcase_package_list')(
        context, {
            'showcase_id': tk.g.pkg_dict['id']
        })

    package_type = DATASET_TYPE_NAME
    return tk.render('showcase/read.html',
                     extra_vars={'dataset_type': package_type})


def manage_datasets_view(id):

    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author
    }
    data_dict = {'id': id}

    try:
        tk.check_access('ckanext_showcase_update', context)
    except tk.NotAuthorized:
        return tk.abort(
            401,
            _('User not authorized to edit {showcase_id}').format(
                showcase_id=id))

    # check if showcase exists
    try:
        tk.g.pkg_dict = tk.get_action('package_show')(context, data_dict)
    except tk.ObjectNotFound:
        return tk.abort(404, _('Showcase not found'))
    except tk.NotAuthorized:
        return tk.abort(401, _('Unauthorized to read showcase'))

    # Are we removing a showcase/dataset association?
    form_data = tk.request.form if tk.check_ckan_version(
        '2.9') else tk.request.params

    if tk.check_ckan_version(min_version='2.9.0'):
        manage_route = 'showcase_blueprint.manage_datasets'
    else:
        manage_route = 'showcase_manage_datasets'

    if (tk.request.method == 'POST'
            and 'bulk_action.showcase_remove' in form_data):
        # Find the datasets to perform the action on, they are prefixed by
        # dataset_ in the form data
        dataset_ids = []
        for param in form_data:
            if param.startswith('dataset_'):
                dataset_ids.append(param[8:])
        if dataset_ids:
            for dataset_id in dataset_ids:
                tk.get_action('ckanext_showcase_package_association_delete')(
                    context, {
                        'showcase_id': tk.g.pkg_dict['id'],
                        'package_id': dataset_id
                    })
            h.flash_success(
                tk.ungettext(
                    "The dataset has been removed from the showcase.",
                    "The datasets have been removed from the showcase.",
                    len(dataset_ids)))
            url = h.url_for(manage_route, id=id)
            return h.redirect_to(url)

    # Are we creating a showcase/dataset association?
    elif (tk.request.method == 'POST'
          and 'bulk_action.showcase_add' in form_data):
        # Find the datasets to perform the action on, they are prefixed by
        # dataset_ in the form data
        dataset_ids = []
        for param in form_data:
            if param.startswith('dataset_'):
                dataset_ids.append(param[8:])
        if dataset_ids:
            successful_adds = []
            for dataset_id in dataset_ids:
                try:
                    tk.get_action(
                        'ckanext_showcase_package_association_create')(
                            context, {
                                'showcase_id': tk.g.pkg_dict['id'],
                                'package_id': dataset_id
                            })
                except tk.ValidationError as e:
                    h.flash_notice(e.error_summary)
                else:
                    successful_adds.append(dataset_id)
            if successful_adds:
                h.flash_success(
                    tk.ungettext(
                        "The dataset has been added to the showcase.",
                        "The datasets have been added to the showcase.",
                        len(successful_adds)))
            url = h.url_for(manage_route, id=id)
            return h.redirect_to(url)

    _add_dataset_search(tk.g.pkg_dict['id'], tk.g.pkg_dict['name'])

    # get showcase packages
    tk.g.showcase_pkgs = tk.get_action('ckanext_showcase_package_list')(
        context, {
            'showcase_id': tk.g.pkg_dict['id']
        })

    return tk.render('showcase/manage_datasets.html')

def _add_dataset_search(showcase_id, showcase_name):
    '''
    Search logic for discovering datasets to add to a showcase.
    '''

    from ckan.lib.search import SearchError

    package_type = 'dataset'

    # unicode format (decoded from utf8)
    q = tk.g.q = tk.request.params.get('q', u'')
    tk.g.query_error = False
    page = h.get_page_number(tk.request.params)

    limit = int(tk.config.get('ckan.datasets_per_page', 20))

    # most search operations should reset the page counter:
    params_nopage = [(k, v) for k, v in tk.request.params.items()
                     if k != 'page']

    def remove_field(key, value=None, replace=None):
        return h.remove_url_param(key,
                                  value=value,
                                  replace=replace,
                                  controller='dataset' if
                                  tk.check_ckan_version('2.9') else 'package',
                                  action='search')

    tk.g.remove_field = remove_field

    sort_by = tk.request.params.get('sort', None)
    params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

    def _sort_by(fields):
        """
        Sort by the given list of fields.

        Each entry in the list is a 2-tuple: (fieldname, sort_order)

        eg - [('metadata_modified', 'desc'), ('name', 'asc')]

        If fields is empty, then the default ordering is used.
        """
        params = params_nosort[:]

        if fields:
            sort_string = ', '.join('%s %s' % f for f in fields)
            params.append(('sort', sort_string))
        return _search_url(params, showcase_name)

    tk.g.sort_by = _sort_by
    if sort_by is None:
        tk.g.sort_by_fields = []
    else:
        tk.g.sort_by_fields = [field.split()[0] for field in sort_by.split(',')]

    def pager_url(q=None, page=None):
        params = list(params_nopage)
        params.append(('page', page))
        return _search_url(params, showcase_name)

    tk.g.search_url_params = urlencode(_encode_params(params_nopage))

    try:
        tk.g.fields = []
        # tk.g.fields_grouped will contain a dict of params containing
        # a list of values eg {'tags':['tag1', 'tag2']}
        tk.g.fields_grouped = {}
        search_extras = {}
        fq = ''
        for (param, value) in tk.request.params.items():
            if param not in ['q', 'page', 'sort'] \
                    and len(value) and not param.startswith('_'):
                if not param.startswith('ext_'):
                    tk.g.fields.append((param, value))
                    fq += ' %s:"%s"' % (param, value)
                    if param not in tk.g.fields_grouped:
                        tk.g.fields_grouped[param] = [value]
                    else:
                        tk.g.fields_grouped[param].append(value)
                else:
                    search_extras[param] = value

        context = {
            'model': model,
            'session': model.Session,
            'user': tk.g.user or tk.g.author,
            'for_view': True,
            'auth_user_obj': tk.g.userobj
        }

        # Unless changed via config options, don't show other dataset
        # types any search page. Potential alternatives are do show them
        # on the default search page (dataset) or on one other search page
        search_all_type = tk.config.get('ckan.search.show_all_types')
        search_all = False

        try:
            # If the "type" is set to True or False, convert to bool
            # and we know that no type was specified, so use traditional
            # behaviour of applying this only to dataset type
            search_all = tk.asbool(search_all_type)
            search_all_type = 'dataset'
        # Otherwise we treat as a string representing a type
        except ValueError:
            search_all = True

        if not search_all or package_type != search_all_type:
            # Only show datasets of this particular type
            fq += ' +dataset_type:{type}'.format(type=package_type)

        # Only search for packages that aren't already associated with the
        # Showcase
        associated_package_ids = ShowcasePackageAssociation.get_package_ids_for_showcase(
            showcase_id)
        # flatten resulting list to space separated string
        if associated_package_ids:
            associated_package_ids_str = \
                ' OR '.join([id[0] for id in associated_package_ids])
            fq += ' !id:({0})'.format(associated_package_ids_str)

        facets = OrderedDict()

        default_facet_titles = {
            'organization': _('Organizations'),
            'groups': _('Groups'),
            'tags': _('Tags'),
            'res_format': _('Formats'),
            'license_id': _('Licenses'),
        }

        # for CKAN-Versions that do not provide the facets-method from
        # helper-context, import facets from ckan.common
        if hasattr(h, 'facets'):
            current_facets = h.facets()
        else:
            from ckan.common import g
            current_facets = g.facets

        for facet in current_facets:
            if facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]
            else:
                facets[facet] = facet

        # Facet titles
        for plugin in p.PluginImplementations(p.IFacets):
            facets = plugin.dataset_facets(facets, package_type)

        tk.g.facet_titles = facets

        data_dict = {
            'q': q,
            'fq': fq.strip(),
            'facet.field': list(facets.keys()),
            'rows': limit,
            'start': (page - 1) * limit,
            'sort': sort_by,
            'extras': search_extras
        }

        query = tk.get_action('package_search')(context, data_dict)
        tk.g.sort_by_selected = query['sort']

        tk.g.page = h.Page(collection=query['results'],
                        page=page,
                        url=pager_url,
                        item_count=query['count'],
                        items_per_page=limit)
        tk.g.facets = query['facets']
        tk.g.search_facets = query['search_facets']
        tk.g.page.items = query['results']
    except SearchError as se:
        log.error('Dataset search error: %r', se.args)
        tk.g.query_error = True
        tk.g.facets = {}
        tk.g.search_facets = {}
        tk.g.page = h.Page(collection=[])
    tk.g.search_facets_limits = {}
    for facet in tk.g.search_facets.keys():
        try:
            limit = int(
                tk.request.params.get(
                    '_%s_limit' % facet,
                    int(tk.config.get('search.facets.default', 10))))
        except tk.ValueError:
            abort(
                400,
                _("Parameter '{parameter_name}' is not an integer").format(
                    parameter_name='_%s_limit' % facet))
        tk.g.search_facets_limits[facet] = limit


def _search_url(params, name):
    url = h.url_for('showcase_manage_datasets', id=name)
    return url_with_params(url, params)


def _encode_params(params):
    return [(k, six.ensure_str(six.text_type(v))) for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def delete_view(id):
    if 'cancel' in tk.request.params:
        tk.redirect_to(
            'showcase_blueprint.edit' if tk.check_ckan_version(min_version='2.9.0')
            else 'showcase_edit', id=id)

    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'auth_user_obj': tk.g.userobj
    }

    try:
        tk.check_access('ckanext_showcase_delete', context, {'id': id})
    except tk.NotAuthorized:
        return tk.abort(401, _('Unauthorized to delete showcase'))

    if tk.check_ckan_version(min_version='2.9.0'):
        index_route = 'showcase_blueprint.index'
    else:
        index_route = 'showcase_index'

    context = {'user': tk.g.user}
    try:
        if tk.request.method == 'POST':
            tk.get_action('ckanext_showcase_delete')(context, {'id': id})
            h.flash_notice(_('Showcase has been deleted.'))
            return tk.redirect_to(index_route)
        tk.g.pkg_dict = tk.get_action('package_show')(context, {'id': id})
    except tk.NotAuthorized:
        tk.abort(401, _('Unauthorized to delete showcase'))
    except tk.ObjectNotFound:
        tk.abort(404, _('Showcase not found'))
    
    return tk.render('showcase/confirm_delete.html',
                     extra_vars={'dataset_type': DATASET_TYPE_NAME})


def dataset_showcase_list(id):
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'for_view': True,
        'auth_user_obj': tk.g.userobj
    }
    data_dict = {'id': id}

    try:
        tk.check_access('package_show', context, data_dict)
    except tk.ObjectNotFound:
        return tk.abort(404, _('Dataset not found'))
    except tk.NotAuthorized:
        return tk.abort(401, _('Not authorized to see this page'))

    try:
        tk.g.pkg_dict = tk.get_action('package_show')(context, data_dict)
        tk.g.showcase_list = tk.get_action('ckanext_package_showcase_list')(
            context, {
                'package_id': tk.g.pkg_dict['id']
            })
    except tk.ObjectNotFound:
        return tk.abort(404, _('Dataset not found'))
    except tk.NotAuthorized:
        return tk.abort(401, _('Unauthorized to read package'))

    if tk.check_ckan_version(min_version='2.9.0'):
        list_route = 'showcase_blueprint.dataset_showcase_list'
    else:
        list_route = 'showcase_dataset_showcase_list'

    if tk.request.method == 'POST':
        # Are we adding the dataset to a showcase?
        form_data = tk.request.form if tk.check_ckan_version(
            '2.9') else tk.request.params

        new_showcase = form_data.get('showcase_added')
        if new_showcase:
            data_dict = {
                "showcase_id": new_showcase,
                "package_id": tk.g.pkg_dict['id']
            }
            try:
                tk.get_action('ckanext_showcase_package_association_create')(
                    context, data_dict)
            except tk.ObjectNotFound:
                return tk.abort(404, _('Showcase not found'))
            else:
                h.flash_success(
                    _("The dataset has been added to the showcase."))

        # Are we removing a dataset from a showcase?
        showcase_to_remove = form_data.get('remove_showcase_id')
        if showcase_to_remove:
            data_dict = {
                "showcase_id": showcase_to_remove,
                "package_id": tk.g.pkg_dict['id']
            }
            try:
                tk.get_action('ckanext_showcase_package_association_delete')(
                    context, data_dict)
            except tk.ObjectNotFound:
                return tk.abort(404, _('Showcase not found'))
            else:
                h.flash_success(
                    _("The dataset has been removed from the showcase."))
        return h.redirect_to(
            h.url_for(list_route, id=tk.g.pkg_dict['name']))

    pkg_showcase_ids = [showcase['id'] for showcase in tk.g.showcase_list]
    site_showcases = tk.get_action('ckanext_showcase_list')(context, {})

    tk.g.showcase_dropdown = [[showcase['id'], showcase['title']]
                           for showcase in site_showcases
                           if showcase['id'] not in pkg_showcase_ids]

    return tk.render("package/dataset_showcase_list.html",
                     extra_vars={'pkg_dict': tk.g.pkg_dict})


def manage_showcase_admins():
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author
    }

    try:
        tk.check_access('sysadmin', context, {})
    except tk.NotAuthorized:
        return tk.abort(401, _('User not authorized to view page'))

    form_data = tk.request.form if tk.check_ckan_version(
        '2.9') else tk.request.params

    if tk.check_ckan_version(min_version='2.9.0'):
        admins_route = 'showcase_blueprint.admins'
    else:
        admins_route = 'showcase_admins'

    # We're trying to add a user to the showcase admins list.
    if tk.request.method == 'POST' and form_data['username']:
        username = form_data['username']
        try:
            tk.get_action('ckanext_showcase_admin_add')(
                {}, {'username': username}
                )
        except tk.NotAuthorized:
            abort(401, _('Unauthorized to perform that action'))
        except tk.ObjectNotFound:
            h.flash_error(
                _("User '{user_name}' not found.").format(user_name=username))
        except tk.ValidationError as e:
            h.flash_notice(e.error_summary)
        else:
            h.flash_success(_("The user is now a Showcase Admin"))

        return tk.redirect_to(h.url_for(admins_route))

    tk.g.showcase_admins = tk.get_action('ckanext_showcase_admin_list')({},{})

    return tk.render('admin/manage_showcase_admins.html')


def remove_showcase_admin():
    '''
    Remove a user from the Showcase Admin list.
    '''
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author
    }

    try:
        tk.check_access('sysadmin', context, {})
    except tk.NotAuthorized:
        return tk.abort(401, _('User not authorized to view page'))

    form_data = tk.request.form if tk.check_ckan_version(
        '2.9') else tk.request.params

    if tk.check_ckan_version(min_version='2.9.0'):
        admins_route = 'showcase_blueprint.admins'
    else:
        admins_route = 'showcase_admins'

    if 'cancel' in form_data:
        return tk.redirect_to(admins_route)

    user_id = tk.request.params['user']
    if tk.request.method == 'POST' and user_id:
        user_id = tk.request.params['user']
        try:
            tk.get_action('ckanext_showcase_admin_remove')(
                {}, {'username': user_id}
                )
        except tk.NotAuthorized:
            return tk.abort(401, _('Unauthorized to perform that action'))
        except tk.ObjectNotFound:
            h.flash_error(_('The user is not a Showcase Admin'))
        else:
            h.flash_success(_('The user is no longer a Showcase Admin'))

        return tk.redirect_to(h.url_for(admins_route))

    tk.g.user_dict = tk.get_action('user_show')({}, {'id': user_id})
    tk.g.user_id = user_id
    return tk.render('admin/confirm_remove_showcase_admin.html')


def markdown_to_html():
    ''' Migrates the notes of all showcases from markdown to html.

    When using CKEditor, notes on showcases are stored in html instead of
    markdown, this command will migrate all nothes using CKAN's
    render_markdown core helper.
    '''
    showcases = tk.get_action('ckanext_showcase_list')({},{})

    site_user = tk.get_action('get_site_user')({
        'model': model,
        'ignore_auth': True},
        {}
    )
    context = {
        'model': model,
        'session': model.Session,
        'ignore_auth': True,
        'user': site_user['name'],
    }

    for showcase in showcases:
        tk.get_action('package_patch')(
            context,
            {
                'id': showcase['id'],
                'notes': h.render_markdown(showcase['notes'])
            }
        )
    log.info('All notes were migrated successfully.')


def upload():
    if not tk.request.method == 'POST':
        tk.abort(409, _('Only Posting is availiable'))

    if ckan_29_or_higher:
        data_dict = logic.clean_dict(
            dict_fns.unflatten(
                logic.tuplize_dict(
                    logic.parse_params(tk.request.files)
                )
            )
        )
    else:
        data_dict = tk.request.POST
    try:

        url = tk.get_action('ckanext_showcase_upload')(
            None,
            data_dict
        )
    except tk.NotAuthorized:
        tk.abort(401, _('Unauthorized to upload file %s') % id)

    return json.dumps(url)
