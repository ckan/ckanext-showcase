import logging

from pylons import config

import ckan.model as model
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
import ckan.lib.render
from ckan.common import c, request, _
from ckan.controllers.package import PackageController

from ckanext.showcase.plugin import DATASET_TYPE_NAME

render = base.render
abort = base.abort
redirect = base.redirect
NotFound = logic.NotFound
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
NotAuthorized = logic.NotAuthorized

log = logging.getLogger(__name__)


class ShowcaseController(PackageController):

    def new(self, data=None, errors=None, error_summary=None):

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params}

        # Check access here, then continue with PackageController.new()
        # PackageController.new will also check access for package_create.
        # This is okay for now, while only sysadmins can create Showcases, but
        # may not work if we allow other users to create Showcases, who don't
        # have access to create dataset package types. Same for edit below.
        try:
            check_access('ckanext_showcase_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a package'))

        return super(ShowcaseController, self).new(data=data, errors=errors,
                                                   error_summary=error_summary)

    def edit(self, id, data=None, errors=None, error_summary=None):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params,
                   'moderated': config.get('moderated'),
                   'pending': True}

        try:
            check_access('ckanext_showcase_update', context)
        except NotAuthorized:
            abort(401, _('User %r not authorized to edit %s') % (c.user, id))

        return super(ShowcaseController, self).edit(id, data=data, errors=errors,
                                                    error_summary=error_summary)

    def _guess_package_type(self, expecting_name=False):
        """Showcase packages are always DATASET_TYPE_NAME."""

        return DATASET_TYPE_NAME

    def _save_new(self, context, package_type=None):
        '''
        The showcase is created then redirects to the manage_dataset page to
        associated packages with the new showcase.
        '''

        data_dict = clean_dict(dict_fns.unflatten(
                tuplize_dict(parse_params(request.POST))))

        data_dict['type'] = package_type
        context['message'] = data_dict.get('log_message', '')

        try:
            pkg_dict = get_action('ckanext_showcase_create')(context, data_dict)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            data_dict['state'] = 'none'
            return self.new(data_dict, errors, error_summary)

        # redirect to add datasets
        url = h.url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='manage_datasets',
                        id=pkg_dict['name'])
        redirect(url)

    def _save_edit(self, name_or_id, context, package_type=None):
        '''
        Edit a showcase's details, then redirect to the showcase read page.
        '''

        data_dict = clean_dict(dict_fns.unflatten(
            tuplize_dict(parse_params(request.POST))))

        data_dict['id'] = name_or_id
        try:
            pkg = get_action('ckanext_showcase_update')(context, data_dict)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.edit(name_or_id, data_dict, errors, error_summary)

        c.pkg_dict = pkg

        # redirect to showcase details page
        url = h.url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='read', id=name_or_id)
        redirect(url)

    def read(self, id, format='html'):
        '''
        Detail view for a single showcase, listing its associated datasets.
        '''

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id}

        # check if showcase exists
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
        except NotFound:
            abort(404, _('Showcase not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read showcase %s') % id)

        # get showcase packages
        c.showcase_pkgs = get_action('ckanext_showcase_package_list')(context, {'showcase_id': c.pkg_dict['id']})

        package_type = DATASET_TYPE_NAME
        self._setup_template_variables(context, {'id': id},
                                       package_type=package_type)

        template = self._read_template(package_type)
        template = template[:template.index('.') + 1] + format

        try:
            return render(template,
                          extra_vars={'dataset_type': package_type})
        except ckan.lib.render.TemplateNotFound:
            msg = _("Viewing {package_type} datasets in {format} format is "
                    "not supported (template file {file} not found)."
                    .format(package_type=package_type, format=format, file=template))
            abort(404, msg)

    def dataset_showcase_list(self, id):
        '''
        Display a list of showcases a dataset is associated with.
        '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id}

        try:
            check_access('package_show', context, data_dict)
        except NotFound:
            abort(404, _('Dataset not found'))
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
            c.showcase_list = get_action('ckanext_package_showcase_list')(context, {'package_id': c.pkg_dict['id']})
        except NotFound:
            abort(404, _('Dataset not found'))
        except logic.NotAuthorized:
            abort(401, _('Unauthorized to read package %s') % id)

        return render("package/dataset_showcase_list.html")

    def manage_datasets(self, id):
        '''
        List datasets associated with the given showcase id.
        '''

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        data_dict = {'id': id}

        try:
            check_access('ckanext_showcase_update', context)
        except NotAuthorized:
            abort(401, _('User %r not authorized to edit %s') % (c.user, id))

        # check if showcase exists
        try:
            c.pkg_dict = get_action('package_show')(context, data_dict)
        except NotFound:
            abort(404, _('Showcase not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read showcase %s') % id)

        # Are we removing a showcase/dataset association?
        if request.method == 'POST' and 'bulk_action.remove' in request.params:
            # Find the datasets to perform the action on, they are prefixed by
            # dataset_ in the form data
            dataset_ids = []
            for param in request.params:
                if param.startswith('dataset_'):
                    dataset_ids.append(param[8:])
            if dataset_ids:
                for dataset_id in dataset_ids:
                    get_action('ckanext_showcase_package_association_delete')(context, {'showcase_id': c.pkg_dict['id'],
                                                                                        'package_id': dataset_id})
                h.flash_notice(_('Dataset has been removed from showcase.'))
                url = h.url_for(controller='ckanext.showcase.controller:ShowcaseController',
                                action='manage_datasets',
                                id=id)
                redirect(url)

        # get showcase packages
        c.showcase_pkgs = get_action('ckanext_showcase_package_list')(context, {'showcase_id': c.pkg_dict['id']})

        package_type = DATASET_TYPE_NAME
        self._setup_template_variables(context, data_dict,
                                       package_type=package_type)

        return render('showcase/manage_datasets.html')
