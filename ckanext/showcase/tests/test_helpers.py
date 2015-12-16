from nose import tools as nosetools
from nose import SkipTest

from ckan.plugins import toolkit as tk
import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

import ckanext.showcase.logic.helpers as showcase_helpers


class TestGetSiteStatistics(helpers.FunctionalTestBase):

    def test_dataset_count_no_datasets(self):
        '''
        Dataset and showcase count is 0 when no datasets, and no showcases.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        stats = showcase_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 0)
        nosetools.assert_equal(stats['showcase_count'], 0)

    def test_dataset_count_no_datasets_some_showcases(self):
        '''
        Dataset and showcase count is 0 when no datasets, but some showcases.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        for i in xrange(0, 10):
            factories.Dataset(type='showcase')

        stats = showcase_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 0)
        nosetools.assert_equal(stats['showcase_count'], 10)

    def test_dataset_count_some_datasets_no_showcases(self):
        '''
        Dataset and showcase count is correct when there are datasets, but no
        showcases.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        for i in xrange(0, 10):
            factories.Dataset()

        stats = showcase_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 10)
        nosetools.assert_equal(stats['showcase_count'], 0)

    def test_dataset_count_some_datasets_some_showcases(self):
        '''
        Dataset and showcase count is correct when there are datasets and some
        showcases.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        for i in xrange(0, 10):
            factories.Dataset()

        for i in xrange(0, 5):
            factories.Dataset(type='showcase')

        stats = showcase_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 10)
        nosetools.assert_equal(stats['showcase_count'], 5)
