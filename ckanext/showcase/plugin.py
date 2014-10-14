import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit

from helpers import showandtell_available
from logic.action import showings_list_admin

log = logging.getLogger(__name__)


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultGroupForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IGroupForm)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'showcase')

    def group_types(self):
        return ["showing"]

    def is_fallback(self):
        return False

    def before_map(self, map):
        map.connect('user_dashboard_showandtell', '/dashboard/showandtell',
                    controller='ckanext.showcase.controller:ShowcaseDashboardController',
                    action='dashboard_showandtell', ckan_icon="bullhorn")
        return map

    def get_helpers(self):
        return {'showandtell_available': showandtell_available}

    def get_actions(self):
        return {'showings_list_admin': showings_list_admin}
