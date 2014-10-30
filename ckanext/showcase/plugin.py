import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit

from routes.mapper import SubMapper

log = logging.getLogger(__name__)

DATASET_TYPE_NAME = 'showcase'


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IRoutes, inherit=True)

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

    def read_template(self):
        return 'showcase/read.html'

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom dataset forms which will use the
        # names below based on the dataset.type ('dataset' is the default type)
        with SubMapper(map, controller='ckanext.showcase.controller:ShowcaseController') as m:
            m.connect('showcase_index', '/showcase', action='search',
                      highlight_actions='index search')
            m.connect('showcase_read', '/showcase/{id}', action='read',
                      ckan_icon='sitemap')

        map.redirect('/showcases', '/showcase')
        map.redirect('/showcases/{url:.*}', '/showcase/{url}')
        return map
