import ckanext.showcase.logic.action.create
import ckanext.showcase.logic.action.delete
import ckanext.showcase.logic.action.update
import ckanext.showcase.logic.action.get


def get_actions():
    action_functions = {
        'ckanext_showcase_create':
            ckanext.showcase.logic.action.create.showcase_create,
        'ckanext_showcase_update':
            ckanext.showcase.logic.action.update.showcase_update,
        'ckanext_showcase_delete':
            ckanext.showcase.logic.action.delete.showcase_delete,
        'ckanext_showcase_show':
            ckanext.showcase.logic.action.get.showcase_show,
        'ckanext_showcase_list':
            ckanext.showcase.logic.action.get.showcase_list,
        'ckanext_showcase_package_association_create':
            ckanext.showcase.logic.action.create.showcase_package_association_create,
        'ckanext_showcase_package_association_delete':
            ckanext.showcase.logic.action.delete.showcase_package_association_delete,
        'ckanext_showcase_package_list':
            ckanext.showcase.logic.action.get.showcase_package_list,
        'ckanext_package_showcase_list':
            ckanext.showcase.logic.action.get.package_showcase_list,
        'ckanext_showcase_admin_add':
            ckanext.showcase.logic.action.create.showcase_admin_add,
        'ckanext_showcase_admin_remove':
            ckanext.showcase.logic.action.delete.showcase_admin_remove,
        'ckanext_showcase_admin_list':
            ckanext.showcase.logic.action.get.showcase_admin_list,
        'ckanext_showcase_upload':
            ckanext.showcase.logic.action.create.showcase_upload,
    }
    return action_functions
