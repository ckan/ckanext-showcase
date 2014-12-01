import ckan.lib.helpers as h


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(key, value=value, replace=replace,
                              controller='ckanext.showcase.controller:ShowcaseController',
                              action='search')
