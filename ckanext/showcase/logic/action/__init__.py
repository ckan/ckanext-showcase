import ckanext.showcase.logic.action.create as CREATE
import ckanext.showcase.logic.action.delete as DELETE
import ckanext.showcase.logic.action.update as UPDATE
import ckanext.showcase.logic.action.get as GET


def get_actions():
    action_functions = {
        # CREATE
        'ckanext_showcase_create': CREATE.showcase_create,
        'ckanext_showcase_package_association_create': CREATE.showcase_package_association_create,
        'ckanext_showcase_upload': CREATE.showcase_upload,
        
        # UPDATE
        'ckanext_showcase_update': UPDATE.showcase_update,
        'ckanext_showcase_status_update': UPDATE.status_update,
        
        # GET
        'ckanext_showcase_show': GET.showcase_show,
        'ckanext_showcase_list': GET.showcase_list,
        'ckanext_showcase_search': GET.showcase_filtered,
        'ckanext_showcase_package_list': GET.showcase_package_list,
        'ckanext_package_showcase_list': GET.package_showcase_list,
        'ckanext_showcase_statics': GET.showcase_statics,
        'ckanext_showcase_status_show': GET.status_show,
        
        # DELETE
        'ckanext_showcase_package_association_delete': DELETE.showcase_package_association_delete,
        'ckanext_showcase_delete': DELETE.showcase_delete,
    }

    return action_functions
