from nose import tools as nosetools

import ckan.model as model
import ckan.plugins.toolkit as toolkit
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

from ckanext.showcase.logic.converters import convert_package_name_or_id_to_title_or_name
from ckanext.showcase.tests import ShowcaseFunctionalTestBase


class TestNameOrIdToTitleConverter(ShowcaseFunctionalTestBase):

    def test_name_to_title(self):
        '''
        Package correctly returns title.
        '''
        context = {'session': model.Session}
        factories.Dataset(id='my-id', title='My Title', name='my-name')

        result = convert_package_name_or_id_to_title_or_name('my-name', context)
        nosetools.assert_equals('My Title', result)

    def test_name_to_name(self):
        '''
        Package with no title correctly returns name.
        '''
        context = {'session': model.Session}
        factories.Dataset(id='my-id', title='', name='my-name')

        result = convert_package_name_or_id_to_title_or_name('my-name', context)
        nosetools.assert_equals('my-name', result)

    def test_id_to_title(self):
        '''
        Package correctly returns title.
        '''
        context = {'session': model.Session}
        factories.Dataset(id='my-id', title='My Title', name='my-name')

        result = convert_package_name_or_id_to_title_or_name('my-id', context)
        nosetools.assert_equals('My Title', result)

    def test_id_to_name(self):
        '''
        Package with no title correctly returns name.
        '''
        context = {'session': model.Session}
        factories.Dataset(id='my-id', title='', name='my-name')

        result = convert_package_name_or_id_to_title_or_name('my-id', context)
        nosetools.assert_equals('my-name', result)

    def test_with_no_package_id_exists(self):
        '''
        No package with id exists. Raises error.
        '''
        context = {'session': model.Session}

        nosetools.assert_raises(toolkit.Invalid, convert_package_name_or_id_to_title_or_name,
                                'my-non-existent-id',
                                context=context)
