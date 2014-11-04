from nose import tools as nosetools

import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

import logging
log = logging.getLogger(__name__)


class TestShowcaseIndex(helpers.FunctionalTestBase):

    def test_showcases_redirects_to_showcase(self):
        '''/showcases redirects to /showcase.'''
        app = self._get_test_app()
        response = app.get('/showcases', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/showcase')

    def test_showcases_redirects_to_showcase_for_item(self):
        '''/showcases/ redirects to /showcase.'''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/showcases/my-showcase', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/showcase/my-showcase')

    def test_showcase_listed_on_index(self):
        '''
        An added Showcase will appear on the Showcase index page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get("/showcase", status=200)
        response.mustcontain("1 showcase found")
        response.mustcontain("my-showcase")
