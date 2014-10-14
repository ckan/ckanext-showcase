import ckan.plugins.toolkit as toolkit


def showandtell_available():
    context = {}
    data_dict = {'available_only': True, 'am_member': True}
    return toolkit.get_action('showings_list_admin')(context, data_dict)
