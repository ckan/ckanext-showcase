from ckan.plugins import toolkit as tk

_ = tk._
Invalid = tk.Invalid


def convert_package_name_or_id_to_id_for_type(package_name_or_id,
                                              context, package_type=None):
    """Convert package name or ID to ID for a specific type.

    This function retrieves the package ID based on the provided name or ID,
    ensuring it matches the specified package type if provided. If no package
    type is specified, it defaults to checking for any package type.

    :param package_name_or_id: The name or ID of the package.
    :param context: The context containing the session and model.
    :param package_type: The type of the package to filter by (optional).
    :returns: The ID of the package.
    :raises: Invalid if no package is found with the given name or ID.
    """
    session = context['session']
    model = context['model']

    dataset_types = tk.aslist(
        package_type or tk.config.get('ckanext.showcase.show_dataset_types', 'dataset')
    )
    if not dataset_types:
        result = model.Package.get(package_name_or_id)
    else:
        result = (
            session.query(model.Package)
            .filter(model.Package.id == package_name_or_id,
                    model.Package.type.in_(dataset_types)).first()
        )

    if not result:
        result = (
            session.query(model.Package)
            .filter(model.Package.id == package_name_or_id,
                    model.Package.type.in_(dataset_types)).first()
        )
    if not result:
        raise Invalid('No package is found with the given name or ID')

    return result.id


def convert_package_name_or_id_to_id_for_type_dataset(package_name_or_id,
                                                      context):
    return convert_package_name_or_id_to_id_for_type(package_name_or_id,
                                                     context)


def convert_package_name_or_id_to_id_for_type_showcase(package_name_or_id,
                                                       context):
    return convert_package_name_or_id_to_id_for_type(package_name_or_id,
                                                     context,
                                                     package_type='showcase')
