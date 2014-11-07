import logging
import json
import socket

import ckan.lib.dictization
import ckan.logic as logic
import ckan.logic.action
import ckan.logic.schema
import ckan.lib.navl.dictization_functions
import ckan.plugins as plugins
import ckan.lib.search as search
import ckan.lib.plugins as lib_plugins

import ckanext.showcase.logic.dictization as showcase_dictize

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_check_access = logic.check_access
NotFound = logic.NotFound
_get_or_bust = logic.get_or_bust


def showcase_show(context, data_dict):

    model = context['model']
    context['session'] = model.Session
    name_or_id = data_dict.get("id") or _get_or_bust(data_dict, 'name_or_id')

    pkg = model.Package.get(name_or_id)

    if pkg is None:
        raise NotFound

    context['package'] = pkg

    _check_access('package_show', context, data_dict)

    if data_dict.get('use_default_schema', False):
        context['schema'] = ckan.logic.schema.default_show_package_schema()

    package_dict = None
    use_cache = (context.get('use_cache', True)
                 and not 'revision_id' in context
                 and not 'revision_date' in context)
    # if use_cache:
    #     log.info('there\'s a cache')
    #     try:
    #         search_result = search.show(name_or_id)
    #     except (search.SearchError, socket.error):
    #         pass
    #     else:
    #         use_validated_cache = 'schema' not in context
    #         if use_validated_cache and 'validated_data_dict' in search_result:
    #             package_dict = json.loads(search_result['validated_data_dict'])
    #             package_dict_validated = True
    #         else:
    #             package_dict = json.loads(search_result['data_dict'])
    #             package_dict_validated = False
    #         metadata_modified = pkg.metadata_modified.isoformat()
    #         search_metadata_modified = search_result['metadata_modified']
    #         # solr stores less precice datetime,
    #         # truncate to 22 charactors to get good enough match
    #         if metadata_modified[:22] != search_metadata_modified[:22]:
    #             package_dict = None

    if not package_dict:
        log.info('There\'s no package_dict')
        package_dict = showcase_dictize.showcase_dictize(pkg, context)
        package_dict_validated = False

    # Add page-view tracking summary data to the package dict.
    # If the package_dict came from the Solr cache then it will already have a
    # potentially outdated tracking_summary, this will overwrite it with a
    # current one.
    package_dict['tracking_summary'] = model.TrackingSummary.get_for_package(
        package_dict['id'])

    # Add page-view tracking summary data to the package's resource dicts.
    # If the package_dict came from the Solr cache then each resource dict will
    # already have a potentially outdated tracking_summary, this will overwrite
    # it with a current one.
    for resource_dict in package_dict['resources']:
        _add_tracking_summary_to_resource_dict(resource_dict, model)

    if context.get('for_view'):
        for item in plugins.PluginImplementations(plugins.IPackageController):
            package_dict = item.before_view(package_dict)

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.read(pkg)

    for resource_dict in package_dict['resources']:
        for item in plugins.PluginImplementations(plugins.IResourceController):
            resource_dict = item.before_show(resource_dict)

    if not package_dict_validated:
        package_plugin = lib_plugins.lookup_package_plugin(
            package_dict['type'])
        if 'schema' in context:
            schema = context['schema']
        else:
            schema = package_plugin.show_package_schema()
            if schema and context.get('validate', True):
                package_dict, errors = lib_plugins.plugin_validate(
                    package_plugin, context, package_dict, schema,
                    'package_show')

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.after_show(context, package_dict)

    return package_dict


def _add_tracking_summary_to_resource_dict(resource_dict, model):
    '''Add page-view tracking summary data to the given resource dict.

    '''
    tracking_summary = model.TrackingSummary.get_for_resource(
        resource_dict['url'])
    resource_dict['tracking_summary'] = tracking_summary
