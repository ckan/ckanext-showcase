import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit

from routes.mapper import SubMapper

log = logging.getLogger(__name__)


class ShowcasePlugin(plugins.SingletonPlugin, lib_plugins.DefaultGroupForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IGroupForm)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'showcase')

    # IGroupForm

    def group_types(self):
        return ['showcase']

    def group_controller(self):
        return 'ckanext.showcase.controller:ShowcaseController'

    def is_fallback(self):
        return False

    def index_template(self):
        return 'showcase/index.html'

    def read_template(self):
        return 'showcase/read.html'

    def about_template(self):
        return 'showcase/about.html'

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom group forms which will use the
        # names below based on the group.type ('group' is the default type)
        with SubMapper(map, controller='ckanext.showcase.controller:ShowcaseController') as m:
            m.connect('showcase_index', '/showcase', action='index',
                      highlight_actions='index search')
            m.connect('showcase_list', '/showcase/list', action='list')
            m.connect('showcase_new', '/showcase/new', action='new')
            m.connect('showcase_action', '/showcase/{action}/{id}',
                      requirements=dict(action='|'.join([
                          'edit',
                          'delete',
                          'member_new',
                          'member_delete',
                          'history',
                          'followers',
                          'follow',
                          'unfollow',
                          'admins',
                          'activity',
                      ])))
            m.connect('showcase_about', '/showcase/about/{id}', action='about',
                      ckan_icon='info-sign'),
            m.connect('showcase_edit', '/showcase/edit/{id}', action='edit',
                      ckan_icon='edit')
            m.connect('showcase_members', '/showcase/members/{id}', action='members',
                      ckan_icon='showcase'),
            m.connect('showcase_activity', '/showcase/activity/{id}/{offset}',
                      action='activity', ckan_icon='time'),
            m.connect('showcase_read', '/showcase/{id}', action='read', ckan_icon='sitemap')

        map.redirect('/showcases', '/showcase')
        map.redirect('/showcases/{url:.*}', '/showcase/{url}')
        return map
