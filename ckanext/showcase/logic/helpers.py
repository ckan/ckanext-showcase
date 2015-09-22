import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.showcase.controller:ShowcaseController',
        action='search')


def get_site_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of showcases.
    '''

    stats = {}
    stats['showcase_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': 'dataset_type:showcase'})['count']
    stats['dataset_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '!dataset_type:showcase'})['count']
    stats['group_count'] = len(tk.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        tk.get_action('organization_list')({}, {}))

    return stats
