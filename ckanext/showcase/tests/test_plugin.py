import mock
from nose import tools as nosetools

import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

import logging
log = logging.getLogger(__name__)


class TestShowcaseIndex(helpers.FunctionalTestBase):

    def test_loggedout_user_cannot_view_showcase(self):
        '''A not logged in user can view the Showcases page.'''
        app = self._get_test_app()
        app.get("/showcase", status=200)

    def test_loggedin_user_can_view_showcase(self):
        '''
        A logged in user can view the Showcases page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/showcase", status=200,
                extra_environ={'REMOTE_USER': str(user["name"])})

    def test_showcases_redirects_to_showcase(self):
        '''/showcases redirects to /showcase.'''
        app = self._get_test_app()
        response = app.get('/showcases', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/showcase')

    # def test_showcases_redirects_to_showcase_for_item(self):
    #     '''/showcases/ redirects to /showcase.'''
    #     app = self._get_test_app()
    #     response = app.get('/showcases', status=302)
    #     nosetools.assert_equal(response.location, 'http://localhost/showcase')

    # @mock.patch('ckan.new_authz.auth_is_loggedin_user')
    # def test_showcase_listed_on_index(self, mockauth):
    #     '''
    #     An added Showcase will appear on the Showcase index page.
    #     '''
    #     app = self._get_test_app()

    #     # Add the Showcase
    #     mockauth.return_value = True
    #     showcase_admin = factories.User()
    #     showcase_group = factories.Group(type='showcase', user=showcase_admin)

    #     response = app.get("/showcase", status=200)
    #     response.mustcontain(showcase_group['name'], "1 showcase found")
