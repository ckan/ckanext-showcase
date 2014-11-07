import logging
import datetime

import ckan.plugins as plugins
import ckan.logic as logic
import ckan.lib.dictization.model_save as model_save
import ckan.lib.plugins as lib_plugins
import ckan.lib.uploader as uploader

from ckan.common import _

log = logging.getLogger(__name__)

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_get_action = logic.get_action
_check_access = logic.check_access
NotFound = logic.NotFound
ValidationError = logic.ValidationError


def showcase_update(context, data_dict):

    model = context['model']
    user = context['user']
    name_or_id = data_dict.get("id") or data_dict['name']

    pkg = model.Package.get(name_or_id)
    if pkg is None:
        raise NotFound(_('Package was not found.'))
    context["package"] = pkg
    data_dict["id"] = pkg.id
    data_dict['type'] = pkg.type

    _check_access('ckanext_showcase_update', context, data_dict)

    # get the schema
    package_plugin = lib_plugins.lookup_package_plugin(pkg.type)
    if 'schema' in context:
        schema = context['schema']
    else:
        schema = package_plugin.update_package_schema()

    upload = uploader.Upload('showcase', pkg._extras['image_url'].value)
    upload.update_data_dict(data_dict, 'image_url',
                            'image_upload', 'clear_upload')

    data, errors = lib_plugins.plugin_validate(
        package_plugin, context, data_dict, schema, 'package_update')
    log.debug('showcase_update validate_errs=%r user=%s package=%s data=%r',
              errors, context.get('user'),
              context.get('package').name if context.get('package') else '',
              data)

    if errors:
        model.Session.rollback()
        raise ValidationError(errors)

    rev = model.repo.new_revision()
    rev.author = user
    if 'message' in context:
        rev.message = context['message']
    else:
        rev.message = _(u'REST API: Update object %s') % data.get("name")

    #avoid revisioning by updating directly
    model.Session.query(model.Package).filter_by(id=pkg.id).update(
        {"metadata_modified": datetime.datetime.utcnow()})
    model.Session.refresh(pkg)

    pkg = model_save.package_dict_save(data, context)

    context_org_update = context.copy()
    context_org_update['ignore_auth'] = True
    context_org_update['defer_commit'] = True
    _get_action('package_owner_org_update')(context_org_update,
                                            {'id': pkg.id,
                                             'organization_id': pkg.owner_org})

    for item in plugins.PluginImplementations(plugins.IPackageController):
        item.edit(pkg)
        item.after_update(context, data)

    upload.upload(uploader.get_max_image_size())
    if not context.get('defer_commit'):
        model.repo.commit()

    log.debug('Updated object %s' % pkg.name)

    return_id_only = context.get('return_id_only', False)

    # Make sure that a user provided schema is not used on package_show
    context.pop('schema', None)

    # we could update the dataset so we should still be able to read it.
    context['ignore_auth'] = True
    output = data_dict['id'] if return_id_only \
        else _get_action('package_show')(context, {'id': data_dict['id']})

    return output
