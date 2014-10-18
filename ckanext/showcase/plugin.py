import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultGroupForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IGroupForm)
    plugins.implements(plugins.IRoutes, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'showcase')

    def group_types(self):
        return ['showcase']

    def group_controller(self):
        return 'ckanext.showcase.controller:ShowcaseController'

    def is_fallback(self):
        return False

    def index_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the index page
        """
        return 'showcase/index.html'

    def before_map(self, map):
        map.connect('showcase_index', '/showcase',
                    controller='ckanext.showcase.controller:ShowcaseController',
                    action='index')
        return map
