import json
from nose import tools as nosetools

import ckan.plugins.toolkit as toolkit
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

from ckanext.showcase.tests import ShowcaseFunctionalTestBase


class TestShowcaseAuthIndex(ShowcaseFunctionalTestBase):

    def test_auth_anon_user_can_view_showcase_index(self):
        '''An anon (not logged in) user can view the Showcases index.'''
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

    def test_auth_anon_user_cant_see_add_showcase_button(self):
        '''
        An anon (not logged in) user can't see the Add Showcase button on the
        showcase index page.
        '''
        app = self._get_test_app()

        response = app.get("/showcase", status=200)

        # test for new showcase link in response
        response.mustcontain(no="/showcase/new")

    def test_auth_logged_in_user_cant_see_add_showcase_button(self):
        '''
        A logged in user can't see the Add Showcase button on the showcase
        index page.
        '''
        app = self._get_test_app()
        user = factories.User()

        response = app.get("/showcase", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for new showcase link in response
        response.mustcontain(no="/showcase/new")

    def test_auth_sysadmin_can_see_add_showcase_button(self):
        '''
        A sysadmin can see the Add Showcase button on the showcase index
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        response = app.get("/showcase", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for new showcase link in response
        response.mustcontain("/showcase/new")


class TestShowcaseAuthDetails(ShowcaseFunctionalTestBase):
    def test_auth_anon_user_can_view_showcase_details(self):
        '''
        An anon (not logged in) user can view an individual Showcase details page.
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

    def test_auth_anon_user_cant_see_manage_button(self):
        '''
        An anon (not logged in) user can't see the Manage button on an individual
        showcase details page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/showcase/my-showcase', status=200)

        # test for url to edit page
        response.mustcontain(no="/showcase/edit/my-showcase")

    def test_auth_logged_in_user_can_see_manage_button(self):
        '''
        A logged in user can't see the Manage button on an individual showcase
        details page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/showcase/my-showcase', status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for url to edit page
        response.mustcontain(no="/showcase/edit/my-showcase")

    def test_auth_sysadmin_can_see_manage_button(self):
        '''
        A sysadmin can see the Manage button on an individual showcase details
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/showcase/my-showcase', status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for url to edit page
        response.mustcontain("/showcase/edit/my-showcase")

    def test_auth_showcase_show_anon_can_access(self):
        '''
        Anon user can request showcase show.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/api/3/action/ckanext_showcase_show?id=my-showcase',
                           status=200)

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_showcase_show_normal_user_can_access(self):
        '''
        Normal logged in user can request showcase show.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/api/3/action/ckanext_showcase_show?id=my-showcase',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_showcase_show_sysadmin_can_access(self):
        '''
        Normal logged in user can request showcase show.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/api/3/action/ckanext_showcase_show?id=my-showcase',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])


class TestShowcaseAuthCreate(ShowcaseFunctionalTestBase):

    def test_auth_anon_user_cant_view_create_showcase(self):
        '''
        An anon (not logged in) user can't access the create showcase page.
        '''
        app = self._get_test_app()
        app.get("/showcase/new", status=302)

    def test_auth_logged_in_user_cant_view_create_showcase_page(self):
        '''
        A logged in user can't access the create showcase page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/showcase/new", status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_create_showcase_page(self):
        '''
        A sysadmin can access the create showcase page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()
        app.get("/showcase/new", status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})


class TestShowcaseAuthList(ShowcaseFunctionalTestBase):

    def test_auth_showcase_list_anon_can_access(self):
        '''
        Anon user can request showcase list.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/api/3/action/ckanext_showcase_list',
                           status=200)

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_showcase_list_normal_user_can_access(self):
        '''
        Normal logged in user can request showcase list.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/api/3/action/ckanext_showcase_list',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_showcase_list_sysadmin_can_access(self):
        '''
        Normal logged in user can request showcase list.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/api/3/action/ckanext_showcase_list',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])


class TestShowcaseAuthEdit(ShowcaseFunctionalTestBase):

    def test_auth_anon_user_cant_view_edit_showcase_page(self):
        '''
        An anon (not logged in) user can't access the showcase edit page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/edit/my-showcase', status=302)

    def test_auth_logged_in_user_cant_view_edit_showcase_page(self):
        '''
        A logged in user can't access the showcase edit page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/edit/my-showcase', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_edit_showcase_page(self):
        '''
        A sysadmin can access the showcase edit page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/edit/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_showcase_admin_can_view_edit_showcase_page(self):
        '''
        A showcase admin can access the showcase edit page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a showcase admin
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/edit/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_manage_datasets(self):
        '''
        An anon (not logged in) user can't access the showcase manage datasets page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/manage_datasets/my-showcase', status=302)

    def test_auth_logged_in_user_cant_view_manage_datasets(self):
        '''
        A logged in user (not sysadmin) can't access the showcase manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/manage_datasets/my-showcase', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_manage_datasets(self):
        '''
        A sysadmin can access the showcase manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/manage_datasets/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_showcase_admin_can_view_manage_datasets(self):
        '''
        A showcase admin can access the showcase manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a showcase admin
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/manage_datasets/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_delete_showcase_page(self):
        '''
        An anon (not logged in) user can't access the showcase delete page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/delete/my-showcase', status=302)

    def test_auth_logged_in_user_cant_view_delete_showcase_page(self):
        '''
        A logged in user can't access the showcase delete page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/delete/my-showcase', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_delete_showcase_page(self):
        '''
        A sysadmin can access the showcase delete page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/delete/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_showcase_admin_can_view_delete_showcase_page(self):
        '''
        A showcase admin can access the showcase delete page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a showcase admin
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='showcase', name='my-showcase')

        app.get('/showcase/delete/my-showcase', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_addtoshowcase_dropdown_dataset_showcase_list(self):
        '''
        An anonymous user can't view the 'Add to showcase' dropdown selector
        from a datasets showcase list page.
        '''
        app = self._get_test_app()

        factories.Dataset(name='my-showcase', type='showcase')
        factories.Dataset(name='my-dataset')

        showcase_list_response = app.get('/dataset/showcases/my-dataset', status=200)

        nosetools.assert_false('showcase-add' in showcase_list_response.forms)

    def test_auth_normal_user_cant_view_addtoshowcase_dropdown_dataset_showcase_list(self):
        '''
        A normal (logged in) user can't view the 'Add to showcase' dropdown
        selector from a datasets showcase list page.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(name='my-showcase', type='showcase')
        factories.Dataset(name='my-dataset')

        showcase_list_response = app.get('/dataset/showcases/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_false('showcase-add' in showcase_list_response.forms)

    def test_auth_sysadmin_can_view_addtoshowcase_dropdown_dataset_showcase_list(self):
        '''
        A sysadmin can view the 'Add to showcase' dropdown selector from a
        datasets showcase list page.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(name='my-showcase', type='showcase')
        factories.Dataset(name='my-dataset')

        showcase_list_response = app.get('/dataset/showcases/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_true('showcase-add' in showcase_list_response.forms)

    def test_auth_showcase_admin_can_view_addtoshowcase_dropdown_dataset_showcase_list(self):
        '''
        A showcase admin can view the 'Add to showcase' dropdown selector from
        a datasets showcase list page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a showcase admin
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        factories.Dataset(name='my-showcase', type='showcase')
        factories.Dataset(name='my-dataset')

        showcase_list_response = app.get('/dataset/showcases/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_true('showcase-add' in showcase_list_response.forms)


class TestShowcasePackageAssociationCreate(ShowcaseFunctionalTestBase):

    def test_showcase_package_association_create_no_user(self):
        '''
        Calling showcase package association create with no user raises
        NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_package_association_create',
                                context=context)

    def test_showcase_package_association_create_sysadmin(self):
        '''
        Calling showcase package association create by a sysadmin doesn't
        raise NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_package_association_create',
                          context=context)

    def test_showcase_package_association_create_showcase_admin(self):
        '''
        Calling showcase package association create by a showcase admin
        doesn't raise NotAuthorized.
        '''
        showcase_admin = factories.User()

        # Make user a showcase admin
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=showcase_admin['name'])

        context = {'user': showcase_admin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_package_association_create',
                          context=context)

    def test_showcase_package_association_create_unauthorized_creds(self):
        '''
        Calling showcase package association create with unauthorized user
        raises NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_package_association_create',
                                context=context)


class TestShowcasePackageAssociationDelete(ShowcaseFunctionalTestBase):

    def test_showcase_package_association_delete_no_user(self):
        '''
        Calling showcase package association create with no user raises
        NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_package_association_delete',
                                context=context)

    def test_showcase_package_association_delete_sysadmin(self):
        '''
        Calling showcase package association create by a sysadmin doesn't
        raise NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_package_association_delete',
                          context=context)

    def test_showcase_package_association_delete_showcase_admin(self):
        '''
        Calling showcase package association create by a showcase admin
        doesn't raise NotAuthorized.
        '''
        showcase_admin = factories.User()

        # Make user a showcase admin
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=showcase_admin['name'])

        context = {'user': showcase_admin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_package_association_delete',
                          context=context)

    def test_showcase_package_association_delete_unauthorized_creds(self):
        '''
        Calling showcase package association create with unauthorized user
        raises NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_package_association_delete',
                                context=context)


class TestShowcaseAdminAddAuth(ShowcaseFunctionalTestBase):

    def test_showcase_admin_add_no_user(self):
        '''
        Calling showcase admin add with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_admin_add', context=context)

    def test_showcase_admin_add_correct_creds(self):
        '''
        Calling showcase admin add by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_admin_add', context=context)

    def test_showcase_admin_add_unauthorized_creds(self):
        '''
        Calling showcase admin add with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_admin_add', context=context)


class TestShowcaseAdminRemoveAuth(ShowcaseFunctionalTestBase):

    def test_showcase_admin_remove_no_user(self):
        '''
        Calling showcase admin remove with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_admin_remove', context=context)

    def test_showcase_admin_remove_correct_creds(self):
        '''
        Calling showcase admin remove by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_admin_remove', context=context)

    def test_showcase_admin_remove_unauthorized_creds(self):
        '''
        Calling showcase admin remove with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_admin_remove', context=context)


class TestShowcaseAdminListAuth(ShowcaseFunctionalTestBase):

    def test_showcase_admin_list_no_user(self):
        '''
        Calling showcase admin list with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_admin_list', context=context)

    def test_showcase_admin_list_correct_creds(self):
        '''
        Calling showcase admin list by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_showcase_admin_list', context=context)

    def test_showcase_admin_list_unauthorized_creds(self):
        '''
        Calling showcase admin list with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_showcase_admin_list', context=context)


class TestShowcaseAuthManageShowcaseAdmins(ShowcaseFunctionalTestBase):

    def test_auth_anon_user_cant_view_showcase_admin_manage_page(self):
        '''
        An anon (not logged in) user can't access the manage showcase admin
        page.
        '''
        app = self._get_test_app()
        app.get("/showcase/new", status=302)

    def test_auth_logged_in_user_cant_view_showcase_admin_manage_page(self):
        '''
        A logged in user can't access the manage showcase admin page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/showcase/new", status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_showcase_admin_manage_page(self):
        '''
        A sysadmin can access the manage showcase admin page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()
        app.get("/showcase/new", status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})
