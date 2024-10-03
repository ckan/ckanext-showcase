import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk
from ckanext.showcase.data.constants import SHOWCASE_STATUS_OPTIONS, ApprovalStatus


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    index_route = 'showcase_blueprint.index'

    return h.remove_url_param(
        key, value=value, replace=replace,
        alternative_url=h.url_for(index_route))


def get_site_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of showcases.
    '''

    stats = {}
    stats['showcase_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '+dataset_type:showcase'})['count']
    stats['dataset_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '!dataset_type:showcase'})['count']
    stats['group_count'] = len(tk.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        tk.get_action('organization_list')({}, {}))

    return stats


def showcase_get_wysiwyg_editor():
    return tk.config.get('ckanext.showcase.editor', '')


def showcase_status_options():
    return [
        {'text': value, 'value':key}
    for key, value in SHOWCASE_STATUS_OPTIONS.items()
    ]



def showcase_status_filter_options():
    return [
        {'text': tk._("Select Status"), 'value': ''}
        ] + showcase_status_options()

_ = tk._
from ckan.common import _, config

def ckanext_showcase_metatdata(showcase, showcase_datasets, user_info):
    return [
        {
            'label': _("Title En"),
            'value': showcase['title'],
            'type': 'text',
        },
        {
            'label': _("Title Ar"),
            'value': showcase['title_ar'],
            'type': 'text',
        },
        {
            'label': _("Slug"),
            'value': showcase['name'],
            'type': 'text',
        },
        {
            'label': _("Description En"),
            'value': h.render_markdown(showcase['notes']),
            'type': 'text',
        },
        {
            'label': _("Description Ar"),
            'value': h.render_markdown(showcase['notes_ar']),
            'type': 'text',
        },
        {
            'label': _("Date Created"),
            'value': showcase['metadata_created'],
            'type': 'date',
        },
        {
            # TODO
            'label': _("Reuse Case Type"),
            'value': [1,2],
            'type': 'list',
        },
        {
            'label': _("The User"),
            'value': user_info['user_dict']['fullname'] or user_info['user_dict']['name'],
            'type': 'text',
        },
        {
            'label': _("Status"),
            'value': showcase['approval_status']['display_status'],
            'type': 'text',
        },
        {
            'label': _("Admin Feedback"),
            'value': showcase['approval_status'].get('feedback',''),
            'type': 'text',
        },
        {
            'label': _("Last Status Update"),
            'value': showcase['approval_status'].get('status_modified',''),
            'type': 'date',
        },
        {
            'label': _("Submitted Author Name"),
            'value': showcase['author'],
            'type': 'text',
        },
        {
            'label': _("Submitted Author Email"),
            'value': showcase['author_email'],
            'type': 'email',
        },
        {
            'label': _("Image Url"),
            'value': showcase['image_display_url'],
            'type': 'link',
            'url': showcase['image_display_url'],
        },
        {
            'label': _("External Link"),
            'value': showcase['url'],
            'type': 'link',
            'url': showcase['url'],
        },
        {
            'label': _("Associated Datasets"),
            'value': "<br>".join([
                f"<a href=\"{h.url_for('dataset.read', id=dataset.get('id'))}\"> {dataset.get('display_name', dataset['title'] )}</a>"
                for dataset in showcase_datasets
                ]),
            'type': 'markup',
        },
        {
            'label': _("Reuse Case Public Display"),
            'value': "Link",
            'type': 'link',
            'url': h.url_for('showcase_blueprint.read', id=showcase['id']),
        },
    ]
