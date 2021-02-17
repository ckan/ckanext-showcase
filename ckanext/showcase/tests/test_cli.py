import ckan.tests.helpers as helpers

try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

from ckan.lib.helpers import render_markdown
from ckanext.showcase.commands.migrate import MigrationCommand


class TestMigrationCommand(object):
    '''Tests for MigrationCommand.markdown_to_html'''

    @classmethod
    def setup_class(cls):
        cls.migration_cmd = MigrationCommand('migration-command')

    def setup(self):
        helpers.reset_db()

    def test_notes_are_migrated_from_markdown_to_html(self):
        showcase1 = factories.Dataset(
            type='showcase',
            name='my-showcase',
            notes='# Title')

        showcase2 = factories.Dataset(
            type='showcase',
            name='my-showcase-2',
            notes='# Title 2')

        self.migration_cmd.args = ['markdown_to_html']
        self.migration_cmd.markdown_to_html()

        migrated_showcase1 = helpers.call_action(
            'package_show',
            context={'ignore_auth': True},
            id=showcase1['id']
        )
        assert(
            migrated_showcase1['notes'] == render_markdown(showcase1['notes'])
            )

        migrated_showcase2 = helpers.call_action(
            'package_show',
            context={'ignore_auth': True},
            id=showcase2['id']
        )
        assert(
            migrated_showcase2['notes'] == render_markdown(showcase2['notes'])
            )
