# -*- coding: utf-8 -*-

from routes.mapper import SubMapper
import ckan.plugins as p


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IRoutes, inherit=True)

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom dataset forms which will use
        # the names below based on the dataset.type ('dataset' is the default
        # type)
        with SubMapper(
                map, controller='ckanext.showcase.controller:ShowcaseController'
        ) as m:
            m.connect('showcase_index', '/showcase', action='search',
                      highlight_actions='index search')
            m.connect('showcase_new', '/showcase/new', action='new')
            m.connect('showcase_delete', '/showcase/delete/{id}',
                      action='delete')
            m.connect('showcase_read', '/showcase/{id}', action='read',
                      ckan_icon='picture')
            m.connect('showcase_edit', '/showcase/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('showcase_manage_datasets',
                      '/showcase/manage_datasets/{id}',
                      action="manage_datasets", ckan_icon="sitemap")
            m.connect('showcase_dataset_showcase_list', '/dataset/showcases/{id}',
                      action='dataset_showcase_list', ckan_icon='picture')
            m.connect('showcase_admins', '/ckan-admin/showcase_admins',
                      action='manage_showcase_admins', ckan_icon='picture'),
            m.connect('showcase_admin_remove',
                      '/ckan-admin/showcase_admin_remove',
                      action='remove_showcase_admin'),
            m.connect('showcase_upload', '/showcase_upload',
                      action='showcase_upload')
        map.redirect('/showcases', '/showcase')
        map.redirect('/showcases/{url:.*}', '/showcase/{url}')
        return map
