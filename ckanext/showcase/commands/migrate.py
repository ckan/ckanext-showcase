from ckan import model
from ckan.lib.cli import CkanCommand
from ckan.lib.munge import munge_title_to_name, substitute_ascii_equivalents
from ckan.logic import get_action


import logging
log = logging.getLogger(__name__)


class MigrationCommand(CkanCommand):
    '''
    CKAN 'Related Items' to 'Showcase' migration command.

    Usage::

        paster showcase migrate -c <path to config file>
            - Migrate Related Items to Showcases

        paster showcase migrate -c <path to config file> [--allow-duplicates]
            - Migrate Related Items to Showcases and allow duplicates

    Must be run from the ckanext-showcase directory.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self,name):
        super(CkanCommand, self).__init__(name)

        self.parser.add_option('--allow-duplicates', dest='allow_duplicates',
                            default=False, help='''Use this option to allow
                            related items with duplicate titles to be migrated.
                            Duplicate showcases will be created as
                            'duplicate_<related-name>_<related-id>'.''', action='store_true')

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(self.__doc__)
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'migrate':
            self.migrate()
        elif cmd == 'make_related':
            self.make_related()
        else:
            print('Command "{0}" not recognized'.format(cmd))

    def migrate(self):
        '''

        '''
        # determine whether migration should allow duplicates
        allow_duplicates = self.options.allow_duplicates

        related_items = get_action('related_list')(data_dict={})

        # preflight:
        # related items must have unique titles before migration
        related_titles = [i['title'] for i in related_items]
        # make a list of duplicate titles
        duplicate_titles = self._find_duplicates(related_titles)
        if duplicate_titles and allow_duplicates == False:
            print(
                """All Related Items must have unique titles before migration. The following
Related Item titles are used more than once and need to be corrected before
migration can continue. Please correct and try again:"""
            )
            for i in duplicate_titles:
                print(i)
            return

        for related in related_items:
            existing_showcase = get_action('package_search')(
                data_dict={'fq': '+dataset_type:showcase original_related_item_id:{0}'.format(related['id'])})
            normalized_title = substitute_ascii_equivalents(related['title'])
            if existing_showcase['count'] > 0:
                print('Showcase for Related Item "{0}" already exists.'.format(
                    normalized_title))
            else:
                showcase_title = self._gen_new_title(related.get('title'), related['id'])
                data_dict = {
                    'original_related_item_id': related.get('id'),
                    'title': showcase_title,
                    'name': munge_title_to_name(showcase_title),
                    'notes': related.get('description'),
                    'image_url': related.get('image_url'),
                    'url': related.get('url'),
                    'tags': [{"name": related.get('type').lower()}]
                }
                # make the showcase
                try:
                    new_showcase = get_action('ckanext_showcase_create')(
                        data_dict=data_dict)
                except Exception as e:
                    print('There was a problem migrating "{0}": {1}'.format(
                        normalized_title, e))
                else:
                    print('Created Showcase from the Related Item "{0}"'.format(normalized_title))

                    # make the showcase_package_association, if needed
                    try:
                        related_pkg_id = self._get_related_dataset(
                            related['id'])
                        if related_pkg_id:
                            get_action('ckanext_showcase_package_association_create')(
                                data_dict={'showcase_id': new_showcase['id'],
                                           'package_id': related_pkg_id})
                    except Exception as e:
                        print('There was a problem creating the showcase_package_association for "{0}": {1}'.format(
                            normalized_title, e))

    def _get_related_dataset(self, related_id):
        '''Get the id of a package from related_dataset, if one exists.'''
        related_dataset = model.Session.query(model.RelatedDataset).filter_by(
            related_id=related_id).first()
        if related_dataset:
            return related_dataset.dataset_id

    def _find_duplicates(self, lst):
        '''From a list, return a set of duplicates.

        >>> MigrationCommand('cmd')._find_duplicates([1, 2, 3, 4, 5])
        []

        >>> MigrationCommand('cmd')._find_duplicates([1, 2, 3, 4, 3, 1, 1])
        [1, 3]

        >>> MigrationCommand('cmd')._find_duplicates(['one', 'two', 'three', 'four', 'two', 'three'])
        ['two', 'three']
        '''
        return list(set(x for x in lst if lst.count(x) >= 2))

    def _gen_new_title(self, title, related_id):
        name = munge_title_to_name(title)
        pkg_obj = model.Session.query(model.Package).filter_by(name=name).first()
        if pkg_obj:
            title.replace('duplicate_', '')
            return 'duplicate_' + title + '_' + related_id
        else:
            return title
