# -*- coding: utf-8 -*-

import pytest

from ckan.lib import helpers
from ckan.tests import factories, helpers as test_helpers

from ckanext.showcase.utils import markdown_to_html


@pytest.mark.usefixtures("clean_db")
class TestUtils(object):

    def test_markdown_to_html(self):
        showcase1 = factories.Dataset(
                type='showcase',
                name='my-showcase',
                notes='# Title')

        showcase2 = factories.Dataset(
            type='showcase',
            name='my-showcase-2',
            notes='# Title 2')

        markdown_to_html()

        migrated_showcase1 = test_helpers.call_action(
                'package_show',
                context={'ignore_auth': True},
                id=showcase1['id']
            )

        assert migrated_showcase1['notes'] == helpers.render_markdown(showcase1['notes'])

        migrated_showcase2 = test_helpers.call_action(
                'package_show',
                context={'ignore_auth': True},
                id=showcase2['id']
            )

        assert migrated_showcase2['notes'] == helpers.render_markdown(showcase2['notes'])
