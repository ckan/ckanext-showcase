import ckan.lib.search as search
import ckan.new_tests.factories as factories
import ckan.new_tests.helpers as helpers


class TestShowcaseAuth(helpers.FunctionalTestBase):

    def setup(self):
        super(TestShowcaseAuth, self).setup()
        # Clear the search index
        # Remove this if #2024 gets merged
        search.clear()

    def test_auth_not_logged_in_user_can_view_showcase_index(self):
        '''A not logged in user can view the Showcases index.'''
        app = self._get_test_app()

        app.get("/showcase", status=200)

    def test_auth_logged_in_user_can_view_showcase_index(self):
        '''
        A logged in user can view the Showcase index.
        '''
        app = self._get_test_app()

        user = factories.User()

        app.get("/showcase", status=200,
                extra_environ={'REMOTE_USER': str(user["name"])})

    def test_auth_not_logged_in_user_can_view_showcase_details(self):
        '''
        A not logged in user can view an individual Showcase details page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/my-showcase', status=200)

    def test_auth_logged_in_user_can_view_showcase_details(self):
        '''
        A logged in user can view an individual Showcase details page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_not_logged_in_user_cant_see_add_showcase_button(self):
        '''
        A not logged in user can't see the Add Showcase button on the
        showcase index page.
        '''
        app = self._get_test_app()

        response = app.get("/showcase", status=200)

        response.mustcontain(no="Add Showcase")

    def test_auth_logged_in_user_cant_see_add_showcase_button(self):
        '''
        A logged in user can't see the Add Showcase button on the showcase
        index page.
        '''
        app = self._get_test_app()
        user = factories.User()

        response = app.get("/showcase", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        response.mustcontain(no="Add Showcase")

    def test_auth_sysadmin_can_see_add_showcase_button(self):
        '''
        A sysadmin can see the Add Showcase button on the showcase index
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        response = app.get("/showcase", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        response.mustcontain("Add Showcase")

    # def test_auth_not_logged_in_user_cant_view_create_showcase(self):
    #     '''
    #     A not logged in user can't access the create showcase page.
    #     '''
    #     assert False

    # def test_auth_logged_in_user_cant_view_create_showcase_page(self):
    #     '''
    #     A logged in user can't access the create showcase page.
    #     '''
    #     assert False

    # def test_auth_sysadmin_can_view_create_showcase_page(self):
    #     '''
    #     A sysadmin can access the create showcase page.
    #     '''
    #     assert False

    # def test_auth_not_logged_in_user_cant_see_manage_button(self):
    #     '''
    #     A not logged in user can't see the Manage button on an individual
    #     showcase details page.
    #     '''
    #     assert False

    # def test_auth_logged_in_user_can_see_manage_button(self):
    #     '''
    #     A logged in user can't see the Manage button on an individual showcase
    #     details page.
    #     '''
    #     assert False

    # def test_auth_sysadmin_can_see_manage_button(self):
    #     '''
    #     A sysadmin can see the Manage button on an individual showcase details
    #     page.
    #     '''
    #     assert False

    # def test_auth_not_logged_in_user_cant_view_edit_showcase_page(self):
    #     '''
    #     A not logged in user can't access the showcase edit page.
    #     '''
    #     assert False

    # def test_auth_logged_in_user_cant_view_edit_showcase_page(self):
    #     '''
    #     A logged in user can't access the showcase edit page.
    #     '''
    #     assert False

    # def test_auth_sysadmin_can_view_edit_showcase_page(self):
    #     '''
    #     A sysadmin can access the showcase edit page.
    #     '''
    #     assert False
