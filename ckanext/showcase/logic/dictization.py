import ckan.lib.helpers as h
import ckan.lib.dictization.model_dictize
import ckan.lib.munge as munge

import logging
log = logging.getLogger(__name__)


def showcase_dictize(pkg, context):
    '''
    Given a Showcase object, returns an equivalent dictionary.

    Gets the appropriate package dictionary and appends showcase specific
    values to it.
    '''

    log.info('my custom dictization')

    result_dict = ckan.lib.dictization.model_dictize.package_dictize(pkg, context)

    image_url = result_dict.get('image_url')
    log.info(image_url)
    result_dict['image_display_url'] = image_url
    if image_url and not image_url.startswith('http'):
        #munge here should not have an effect only doing it incase
        #of potential vulnerability of dodgy api input
        image_url = munge.munge_filename(image_url)
        result_dict['image_display_url'] = h.url_for_static(
            'uploads/group/%s' % result_dict.get('image_url'),
            qualified=True
        )

    return result_dict
