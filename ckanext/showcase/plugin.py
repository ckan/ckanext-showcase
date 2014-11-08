import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.lib.munge as munge
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from ckan.common import OrderedDict, _

from routes.mapper import SubMapper

import ckanext.showcase.logic.auth
import ckanext.showcase.logic.action.create
import ckanext.showcase.logic.action.update
import ckanext.showcase.logic.action.get

log = logging.getLogger(__name__)

DATASET_TYPE_NAME = 'showcase'


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'showcase')

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
        log.info('showcase plugin create_package_schema')
        schema = super(ShowcasePlugin, self).create_package_schema()
        schema.update({
            'image_url': [toolkit.get_validator('ignore_missing'),
                          toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def update_package_schema(self):
        log.info('showcase plugin update_package_schema')
        schema = super(ShowcasePlugin, self).update_package_schema()
        schema.update({
            'image_url': [toolkit.get_validator('ignore_missing'),
                          toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def show_package_schema(self):
        log.info('showcase plugin show_package_schema')
        schema = super(ShowcasePlugin, self).show_package_schema()
        schema.update({
            'image_url': [toolkit.get_converter('convert_from_extras'),
                          toolkit.get_validator('ignore_missing')]
        })
        return schema

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        if package_type != DATASET_TYPE_NAME:
            return facets_dict
        return OrderedDict({'tags': _('Tags')})

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'ckanext_showcase_create': ckanext.showcase.logic.auth.create,
            'ckanext_showcase_update': ckanext.showcase.logic.auth.update
        }

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom dataset forms which will use the
        # names below based on the dataset.type ('dataset' is the default type)
        with SubMapper(map, controller='ckanext.showcase.controller:ShowcaseController') as m:
            m.connect('showcase_index', '/showcase', action='search',
                      highlight_actions='index search')
            m.connect('add showcase', '/showcase/new', action='new')
            m.connect('showcase_read', '/showcase/{id}', action='read',
                      ckan_icon='sitemap')
            m.connect('showcase_edit', '/showcase/edit/{id}', action='edit',
                      ckan_icon='edit')
        map.redirect('/showcases', '/showcase')
        map.redirect('/showcases/{url:.*}', '/showcase/{url}')
        return map

    # IActions

    def get_actions(self):
        action_functions = {
            'ckanext_showcase_create': ckanext.showcase.logic.action.create.showcase_create,
            'ckanext_showcase_update': ckanext.showcase.logic.action.update.showcase_update
        }
        return action_functions

    # IPackageController

    def after_show(self, context, pkg_dict):
        image_url = pkg_dict.get('image_url')
        pkg_dict['image_display_url'] = image_url
        if image_url and not image_url.startswith('http'):
            #munge here should not have an effect only doing it incase
            #of potential vulnerability of dodgy api input
            pkg_dict['image_url'] = munge.munge_filename(image_url)
            pkg_dict['image_display_url'] = \
                h.url_for_static('uploads/{0}/{1}'
                                 .format(DATASET_TYPE_NAME, pkg_dict.get('image_url')),
                                 qualified=True)
