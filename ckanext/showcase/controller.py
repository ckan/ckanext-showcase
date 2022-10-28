import logging
import json


from ckan.plugins import toolkit as tk
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dict_fns
import ckan.logic as logic
from ckan.controllers.package import (PackageController)


from ckanext.showcase import utils
from ckanext.showcase.utils import DATASET_TYPE_NAME

_ = tk._
c = tk.c
request = tk.request
render = tk.render
abort = tk.abort
redirect = tk.redirect_to
NotFound = tk.ObjectNotFound
ValidationError = tk.ValidationError
check_access = tk.check_access
get_action = tk.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
NotAuthorized = tk.NotAuthorized

log = logging.getLogger(__name__)


class ShowcaseController(PackageController):
    def new(self, data=None, errors=None, error_summary=None):

        utils.check_new_view_auth()
        return super(ShowcaseController, self).new(data=data,
                                                   errors=errors,
                                                   error_summary=error_summary)

    def edit(self, id, data=None, errors=None, error_summary=None):
        utils.check_edit_view_auth(id)
        return super(ShowcaseController,
                     self).edit(id,
                                data=data,
                                errors=errors,
                                error_summary=error_summary)

    def _guess_package_type(self, expecting_name=False):
        """Showcase packages are always DATASET_TYPE_NAME."""

        return DATASET_TYPE_NAME

    def _save_new(self, context, package_type=None):
        '''
        The showcase is created then redirects to the manage_dataset page to
        associated packages with the new showcase.
        '''

        data_dict = clean_dict(
            dict_fns.unflatten(tuplize_dict(parse_params(request.POST))))

        data_dict['type'] = package_type

        try:
            pkg_dict = get_action('ckanext_showcase_create')(context,
                                                             data_dict)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            data_dict['state'] = 'none'
            return self.new(data_dict, errors, error_summary)

        # redirect to manage datasets
        url = h.url_for('showcase_manage_datasets', id=pkg_dict['name'])
        redirect(url)

    def _save_edit(self, name_or_id, context, package_type=None):
        '''
        Edit a showcase's details, then redirect to the showcase read page.
        '''

        data_dict = clean_dict(
            dict_fns.unflatten(tuplize_dict(parse_params(request.POST))))

        data_dict['id'] = name_or_id
        try:
            pkg = get_action('ckanext_showcase_update')(context, data_dict)
        except ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.edit(name_or_id, data_dict, errors, error_summary)

        c.pkg_dict = pkg

        # redirect to showcase details page
        url = h.url_for('showcase_read', id=pkg['name'])
        redirect(url)

    def read(self, id, format='html'):
        '''
        Detail view for a single showcase, listing its associated datasets.
        '''

        return utils.read_view(id)

    def delete(self, id):
        return utils.delete_view(id)

    def dataset_showcase_list(self, id):
        '''
        Display a list of showcases a dataset is associated with, with an
        option to add to showcase from a list.
        '''
        return utils.dataset_showcase_list(id)

    def manage_datasets(self, id):
        '''
        List datasets associated with the given showcase id.
        '''
        return utils.manage_datasets_view(id)

    def manage_showcase_admins(self):
        return utils.manage_showcase_admins()

    def remove_showcase_admin(self):
        return utils.remove_showcase_admin()

    def showcase_upload(self):
        return utils.upload()
