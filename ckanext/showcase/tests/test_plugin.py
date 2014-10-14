import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

import ckanext.showcase.plugin as plugin

import logging
log = logging.getLogger(__name__)


class TestShowAndTellDashboard(helpers.FunctionalTestBase):

    def test_loggedout_user_cannot_view_dashboard(self):
        '''A not logged in user will not be able to view the dashboard.'''
        app = self._get_test_app()
        app.get("/dashboard", status=404)

    def test_loggedin_user_can_view_dashboard(self):
        '''
        A logged in user will be able to view the dashboard that contains a
        link to the Show & Tell page.
        '''
        app = self._get_test_app()
        user = factories.User()
        response = app.get("/dashboard", status=200,
                           extra_environ={'REMOTE_USER': str(user["name"])})
        response.mustcontain('My Show &amp; Tell')

    def test_loggedout_user_cannot_view_dashboard_showandtell(self):
        '''
        A not logged in user will not be able to view the dashboard
        showandtell page.
        '''
        app = self._get_test_app()
        app.get("/dashboard/showandtell", status=404)

    def test_loggedin_user_can_view_dashboard_showandtell(self):
        '''
        A logged in user will be able to view their dashboard showandtell
        page.
        '''
        app = self._get_test_app()
        user = factories.User()
        response = app.get("/dashboard/showandtell", status=200,
                           extra_environ={'REMOTE_USER': str(user["name"])})
        response.mustcontain('My Show &amp; Tell')
