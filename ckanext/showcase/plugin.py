import logging

from pylons import c
import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from ckan.common import OrderedDict, _
from ckan import model as ckan_model

from routes.mapper import SubMapper

import ckanext.showcase.logic.auth
import ckanext.showcase.logic.action.create
import ckanext.showcase.logic.action.delete
import ckanext.showcase.logic.action.update
import ckanext.showcase.logic.action.get
import ckanext.showcase.logic.schema as showcase_schema
import ckanext.showcase.logic.helpers as showcase_helpers
from ckanext.showcase.model import setup as model_setup


log = logging.getLogger(__name__)

DATASET_TYPE_NAME = 'showcase'


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        # If ckan is more than 2.3, use the 2.4+ toolkit method
        if not toolkit.check_ckan_version(max_version='2.3'):
            toolkit.add_ckan_admin_tab(config, 'ckanext_showcase_admins', 'Showcase Config')

    # IConfigurable

    def configure(self, config):
        model_setup()

    # IDatasetForm

    def package_types(self):
        return [DATASET_TYPE_NAME]

    def is_fallback(self):
        return False

    def search_template(self):
        return 'showcase/search.html'

    def new_template(self):
        return 'showcase/new.html'

    def read_template(self):
        return 'showcase/read.html'

    def edit_template(self):
        return 'showcase/edit.html'

    def package_form(self):
        return 'showcase/new_package_form.html'

    def create_package_schema(self):
        return showcase_schema.showcase_create_schema()

    def update_package_schema(self):
        return showcase_schema.showcase_update_schema()

    def show_package_schema(self):
        return showcase_schema.showcase_show_schema()

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'facet_remove_field': showcase_helpers.facet_remove_field,
            'get_site_statistics': showcase_helpers.get_site_statistics
        }

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        '''Only show tags for Showcase search list.'''
        if package_type != DATASET_TYPE_NAME:
            return facets_dict
        return OrderedDict({'tags': _('Tags')})

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'ckanext_showcase_create': ckanext.showcase.logic.auth.create,
            'ckanext_showcase_update': ckanext.showcase.logic.auth.update,
            'ckanext_showcase_delete': ckanext.showcase.logic.auth.delete,
            'ckanext_showcase_show': ckanext.showcase.logic.auth.show,
            'ckanext_showcase_list': ckanext.showcase.logic.auth.list,
            'ckanext_showcase_package_association_create': ckanext.showcase.logic.auth.package_association_create,
            'ckanext_showcase_package_association_delete': ckanext.showcase.logic.auth.package_association_delete,
            'ckanext_showcase_package_list': ckanext.showcase.logic.auth.showcase_package_list,
            'ckanext_package_showcase_list': ckanext.showcase.logic.auth.package_showcase_list,
            'ckanext_showcase_admin_add': ckanext.showcase.logic.auth.add_showcase_admin,
            'ckanext_showcase_admin_remove': ckanext.showcase.logic.auth.remove_showcase_admin,
            'ckanext_showcase_admin_list': ckanext.showcase.logic.auth.showcase_admin_list
        }

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom dataset forms which will use the
        # names below based on the dataset.type ('dataset' is the default type)
        with SubMapper(map, controller='ckanext.showcase.controller:ShowcaseController') as m:
            m.connect('ckanext_showcase_index', '/showcase', action='search',
                      highlight_actions='index search')
            m.connect('ckanext_showcase_new', '/showcase/new', action='new')
            m.connect('ckanext_showcase_delete', '/showcase/delete/{id}', action='delete')
            m.connect('ckanext_showcase_read', '/showcase/{id}', action='read',
                      ckan_icon='picture')
            m.connect('ckanext_showcase_edit', '/showcase/edit/{id}', action='edit',
                      ckan_icon='edit')
            m.connect('ckanext_showcase_manage_datasets', '/showcase/manage_datasets/{id}',
                      action="manage_datasets", ckan_icon="sitemap")
            m.connect('dataset_showcase_list', '/dataset/showcases/{id}',
                      action='dataset_showcase_list', ckan_icon='picture')
            m.connect('ckanext_showcase_admins', '/ckan-admin/showcase_admins',
                      action='manage_showcase_admins', ckan_icon='picture'),
            m.connect('ckanext_showcase_admin_remove', '/ckan-admin/showcase_admin_remove',
                      action='remove_showcase_admin')
        map.redirect('/showcases', '/showcase')
        map.redirect('/showcases/{url:.*}', '/showcase/{url}')
        return map

    # IActions

    def get_actions(self):
        action_functions = {
            'ckanext_showcase_create': ckanext.showcase.logic.action.create.showcase_create,
            'ckanext_showcase_update': ckanext.showcase.logic.action.update.showcase_update,
            'ckanext_showcase_delete': ckanext.showcase.logic.action.delete.showcase_delete,
            'ckanext_showcase_show': ckanext.showcase.logic.action.get.showcase_show,
            'ckanext_showcase_list': ckanext.showcase.logic.action.get.showcase_list,
            'ckanext_showcase_package_association_create': ckanext.showcase.logic.action.create.showcase_package_association_create,
            'ckanext_showcase_package_association_delete': ckanext.showcase.logic.action.delete.showcase_package_association_delete,
            'ckanext_showcase_package_list': ckanext.showcase.logic.action.get.showcase_package_list,
            'ckanext_package_showcase_list': ckanext.showcase.logic.action.get.package_showcase_list,
            'ckanext_showcase_admin_add': ckanext.showcase.logic.action.create.showcase_admin_add,
            'ckanext_showcase_admin_remove': ckanext.showcase.logic.action.delete.showcase_admin_remove,
            'ckanext_showcase_admin_list': ckanext.showcase.logic.action.get.showcase_admin_list,
        }
        return action_functions

    # IPackageController

    def _add_to_pkg_dict(self, context, pkg_dict):
        '''
        Add key/values to pkg_dict and return it.
        '''

        if pkg_dict['type'] != 'showcase':
            return pkg_dict

        # Add a display url for the Showcase image to the pkg dict so template
        # has access to it.
        image_url = pkg_dict.get('image_url')
        pkg_dict[u'image_display_url'] = image_url
        if image_url and not image_url.startswith('http'):
            pkg_dict[u'image_url'] = image_url
            pkg_dict[u'image_display_url'] = \
                h.url_for_static('uploads/{0}/{1}'
                                 .format(DATASET_TYPE_NAME, pkg_dict.get('image_url')),
                                 qualified=True)

        # Add dataset count
        pkg_dict[u'num_datasets'] = len(toolkit.get_action('ckanext_showcase_package_list')
                                                          (context, {'showcase_id': pkg_dict['id']}))

        # Rendered notes
        pkg_dict[u'showcase_notes_formatted'] = h.render_markdown(pkg_dict['notes'])
        return pkg_dict

    def after_show(self, context, pkg_dict):
        '''
        Modify package_show pkg_dict.
        '''
        pkg_dict = self._add_to_pkg_dict(context, pkg_dict)

    def before_view(self, pkg_dict):
        '''
        Modify pkg_dict that is sent to templates.
        '''

        context = {'model': ckan_model, 'session': ckan_model.Session,
                   'user': c.user or c.author}

        return self._add_to_pkg_dict(context, pkg_dict)

    def before_search(self, search_params):
        '''
        Unless the query is already being filtered by this dataset_type
        (either positively, or negatively), exclude datasets of type
        `showcase`.
        '''
        fq = search_params.get('fq', '')
        if 'dataset_type:{0}'.format(DATASET_TYPE_NAME) not in fq:
            fq = "{0} -dataset_type:{1}".format(search_params.get('fq', ''),
                                                DATASET_TYPE_NAME)
            search_params.update({'fq': fq})
        return search_params
