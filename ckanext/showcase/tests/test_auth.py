import pytest
import json

import ckan.plugins.toolkit as toolkit

from ckan.tests import factories, helpers


def _get_request(app, url, status):
    ''' Wrapper around app.get() for compatibility between CKAN versions.

    CKAN 2.9's app.get() forces a redirect and 2.8's doesn't. Also
    follow_redirects parameter is not supported in CKAN 2.8.

    Can be removed when CKAN 2.8 is no longer supported.
    '''
    try:
        # CKAN 2.9
        app.get(url, status=status, follow_redirects=False)
    except TypeError:
        # CKAN 2.8
        app.get(url, status=status)


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAuthIndex(object):
    def test_auth_anon_user_can_view_showcase_index(self, app):
        """An anon (not logged in) user can view the Showcases index."""

        app.get("/showcase", status=200)

    def test_auth_logged_in_user_can_view_showcase_index(self, app):
        """
        A logged in user can view the Showcase index.
        """

        user = factories.User()

        app.get(
            "/showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_anon_user_cant_see_add_showcase_button(self, app):
        """
        An anon (not logged in) user can't see the Add Showcase button on the
        showcase index page.
        """

        response = app.get("/showcase", status=200)

        # test for new showcase link in response
        assert "/showcase/new" not in response.body

    def test_auth_logged_in_user_cant_see_add_showcase_button(self, app):
        """
        A logged in user can't see the Add Showcase button on the showcase
        index page.
        """

        user = factories.User()

        response = app.get(
            "/showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        # test for new showcase link in response
        assert "/showcase/new" not in response.body

    def test_auth_sysadmin_can_see_add_showcase_button(self, app):
        """
        A sysadmin can see the Add Showcase button on the showcase index
        page.
        """

        user = factories.Sysadmin()

        response = app.get(
            "/showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        # test for new showcase link in response
        assert "/showcase/new" in response.body


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAuthDetails(object):
    def test_auth_anon_user_can_view_showcase_details(self, app):
        """
        An anon (not logged in) user can view an individual Showcase details page.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        app.get("/showcase/my-showcase", status=200)

    def test_auth_logged_in_user_can_view_showcase_details(self, app):
        """
        A logged in user can view an individual Showcase details page.
        """

        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_anon_user_cant_see_manage_button(self, app):
        """
        An anon (not logged in) user can't see the Manage button on an individual
        showcase details page.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get("/showcase/my-showcase", status=200)

        assert "/showcase/edit/my-showcase" not in response.body

    def test_auth_logged_in_user_can_see_manage_button(self, app):
        """
        A logged in user can't see the Manage button on an individual showcase
        details page.
        """

        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/showcase/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        # test for url to edit page
        assert "/showcase/edit/my-showcase" not in response.body

    def test_auth_sysadmin_can_see_manage_button(self, app):
        """
        A sysadmin can see the Manage button on an individual showcase details
        page.
        """

        user = factories.Sysadmin()

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/showcase/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        # test for url to edit page
        assert "/showcase/edit/my-showcase" in response.body

    def test_auth_showcase_show_anon_can_access(self, app):
        """
        Anon user can request showcase show.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/api/3/action/ckanext_showcase_show?id=my-showcase", status=200
        )

        json_response = json.loads(response.body)

        assert json_response["success"]

    def test_auth_showcase_show_normal_user_can_access(self, app):
        """
        Normal logged in user can request showcase show.
        """
        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/api/3/action/ckanext_showcase_show?id=my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        json_response = json.loads(response.body)

        assert json_response["success"]

    def test_auth_showcase_show_sysadmin_can_access(self, app):
        """
        Normal logged in user can request showcase show.
        """
        user = factories.Sysadmin()

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/api/3/action/ckanext_showcase_show?id=my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        json_response = json.loads(response.body)

        assert json_response["success"]


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAuthCreate(object):
    def test_auth_anon_user_cant_view_create_showcase(self, app):
        """
        An anon (not logged in) user can't access the create showcase page.
        """
        _get_request(app, "/showcase/new", status=302)

    def test_auth_logged_in_user_cant_view_create_showcase_page(self, app):
        """
        A logged in user can't access the create showcase page.
        """
        user = factories.User()
        app.get(
            "/showcase/new",
            status=401,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_sysadmin_can_view_create_showcase_page(self, app):
        """
        A sysadmin can access the create showcase page.
        """
        user = factories.Sysadmin()
        app.get(
            "/showcase/new",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAuthList(object):
    def test_auth_showcase_list_anon_can_access(self, app):
        """
        Anon user can request showcase list.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get("/api/3/action/ckanext_showcase_list", status=200)

        json_response = json.loads(response.body)

        assert json_response["success"]

    def test_auth_showcase_list_normal_user_can_access(self, app):
        """
        Normal logged in user can request showcase list.
        """
        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/api/3/action/ckanext_showcase_list",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        json_response = json.loads(response.body)

        assert json_response["success"]

    def test_auth_showcase_list_sysadmin_can_access(self, app):
        """
        Normal logged in user can request showcase list.
        """
        user = factories.Sysadmin()

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get(
            "/api/3/action/ckanext_showcase_list",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        json_response = json.loads(response.body)

        assert json_response["success"]


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAuthEdit(object):
    def test_auth_anon_user_cant_view_edit_showcase_page(self, app):
        """
        An anon (not logged in) user can't access the showcase edit page.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        _get_request(app, "/showcase/edit/my-showcase", status=302)

    def test_auth_logged_in_user_cant_view_edit_showcase_page(self, app):
        """
        A logged in user can't access the showcase edit page.
        """

        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/edit/my-showcase",
            status=401,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_sysadmin_can_view_edit_showcase_page(self, app):
        """
        A sysadmin can access the showcase edit page.
        """

        user = factories.Sysadmin()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/edit/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_showcase_admin_can_view_edit_showcase_page(self, app):
        """
        A showcase admin can access the showcase edit page.
        """

        user = factories.User()

        # Make user a showcase admin
        helpers.call_action(
            "ckanext_showcase_admin_add", context={}, username=user["name"]
        )

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/edit/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_anon_user_cant_view_manage_datasets(self, app):
        """
        An anon (not logged in) user can't access the showcase manage datasets page.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        _get_request(app, "/showcase/manage_datasets/my-showcase", status=302)

    def test_auth_logged_in_user_cant_view_manage_datasets(self, app):
        """
        A logged in user (not sysadmin) can't access the showcase manage datasets page.
        """

        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/manage_datasets/my-showcase",
            status=401,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_sysadmin_can_view_manage_datasets(self, app):
        """
        A sysadmin can access the showcase manage datasets page.
        """

        user = factories.Sysadmin()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/manage_datasets/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_showcase_admin_can_view_manage_datasets(self, app):
        """
        A showcase admin can access the showcase manage datasets page.
        """

        user = factories.User()

        # Make user a showcase admin
        helpers.call_action(
            "ckanext_showcase_admin_add", context={}, username=user["name"]
        )

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/manage_datasets/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_anon_user_cant_view_delete_showcase_page(self, app):
        """
        An anon (not logged in) user can't access the showcase delete page.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        _get_request(app, "/showcase/delete/my-showcase", status=302)

    def test_auth_logged_in_user_cant_view_delete_showcase_page(self, app):
        """
        A logged in user can't access the showcase delete page.
        """

        user = factories.User()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/delete/my-showcase",
            status=401,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_sysadmin_can_view_delete_showcase_page(self, app):
        """
        A sysadmin can access the showcase delete page.
        """

        user = factories.Sysadmin()

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/delete/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_showcase_admin_can_view_delete_showcase_page(self, app):
        """
        A showcase admin can access the showcase delete page.
        """

        user = factories.User()

        # Make user a showcase admin
        helpers.call_action(
            "ckanext_showcase_admin_add", context={}, username=user["name"]
        )

        factories.Dataset(type="showcase", name="my-showcase")

        app.get(
            "/showcase/delete/my-showcase",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_anon_user_cant_view_addtoshowcase_dropdown_dataset_showcase_list(
        self, app
    ):
        """
        An anonymous user can't view the 'Add to showcase' dropdown selector
        from a datasets showcase list page.
        """

        factories.Dataset(name="my-showcase", type="showcase")
        factories.Dataset(name="my-dataset")

        showcase_list_response = app.get(
            "/dataset/showcases/my-dataset", status=200
        )

        assert "showcase-add" not in showcase_list_response.body

    def test_auth_normal_user_cant_view_addtoshowcase_dropdown_dataset_showcase_list(
        self, app
    ):
        """
        A normal (logged in) user can't view the 'Add to showcase' dropdown
        selector from a datasets showcase list page.
        """
        user = factories.User()

        factories.Dataset(name="my-showcase", type="showcase")
        factories.Dataset(name="my-dataset")

        showcase_list_response = app.get(
            "/dataset/showcases/my-dataset",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        assert "showcase-add" not in showcase_list_response.body

    def test_auth_sysadmin_can_view_addtoshowcase_dropdown_dataset_showcase_list(
        self, app
    ):
        """
        A sysadmin can view the 'Add to showcase' dropdown selector from a
        datasets showcase list page.
        """
        user = factories.Sysadmin()

        factories.Dataset(name="my-showcase", type="showcase")
        factories.Dataset(name="my-dataset")

        showcase_list_response = app.get(
            "/dataset/showcases/my-dataset",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        assert "showcase-add" in showcase_list_response.body

    def test_auth_showcase_admin_can_view_addtoshowcase_dropdown_dataset_showcase_list(
        self, app
    ):
        """
        A showcase admin can view the 'Add to showcase' dropdown selector from
        a datasets showcase list page.
        """

        user = factories.User()

        # Make user a showcase admin
        helpers.call_action(
            "ckanext_showcase_admin_add", context={}, username=user["name"]
        )

        factories.Dataset(name="my-showcase", type="showcase")
        factories.Dataset(name="my-dataset")

        showcase_list_response = app.get(
            "/dataset/showcases/my-dataset",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

        assert "showcase-add" in showcase_list_response.body


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcasePackageAssociationCreate(object):
    def test_showcase_package_association_create_no_user(self):
        """
        Calling showcase package association create with no user raises
        NotAuthorized.
        """

        context = {"user": None, "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_package_association_create", context=context,
            )

    def test_showcase_package_association_create_sysadmin(self):
        """
        Calling showcase package association create by a sysadmin doesn't
        raise NotAuthorized.
        """
        a_sysadmin = factories.Sysadmin()
        context = {"user": a_sysadmin["name"], "model": None}
        helpers.call_auth(
            "ckanext_showcase_package_association_create", context=context
        )

    def test_showcase_package_association_create_showcase_admin(self):
        """
        Calling showcase package association create by a showcase admin
        doesn't raise NotAuthorized.
        """
        showcase_admin = factories.User()

        # Make user a showcase admin
        helpers.call_action(
            "ckanext_showcase_admin_add",
            context={},
            username=showcase_admin["name"],
        )

        context = {"user": showcase_admin["name"], "model": None}
        helpers.call_auth(
            "ckanext_showcase_package_association_create", context=context
        )

    def test_showcase_package_association_create_unauthorized_creds(self):
        """
        Calling showcase package association create with unauthorized user
        raises NotAuthorized.
        """
        not_a_sysadmin = factories.User()
        context = {"user": not_a_sysadmin["name"], "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_package_association_create", context=context,
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcasePackageAssociationDelete(object):
    def test_showcase_package_association_delete_no_user(self):
        """
        Calling showcase package association create with no user raises
        NotAuthorized.
        """

        context = {"user": None, "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_package_association_delete", context=context,
            )

    def test_showcase_package_association_delete_sysadmin(self):
        """
        Calling showcase package association create by a sysadmin doesn't
        raise NotAuthorized.
        """
        a_sysadmin = factories.Sysadmin()
        context = {"user": a_sysadmin["name"], "model": None}
        helpers.call_auth(
            "ckanext_showcase_package_association_delete", context=context
        )

    def test_showcase_package_association_delete_showcase_admin(self):
        """
        Calling showcase package association create by a showcase admin
        doesn't raise NotAuthorized.
        """
        showcase_admin = factories.User()

        # Make user a showcase admin
        helpers.call_action(
            "ckanext_showcase_admin_add",
            context={},
            username=showcase_admin["name"],
        )

        context = {"user": showcase_admin["name"], "model": None}
        helpers.call_auth(
            "ckanext_showcase_package_association_delete", context=context
        )

    def test_showcase_package_association_delete_unauthorized_creds(self):
        """
        Calling showcase package association create with unauthorized user
        raises NotAuthorized.
        """
        not_a_sysadmin = factories.User()
        context = {"user": not_a_sysadmin["name"], "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_package_association_delete", context=context,
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAdminAddAuth(object):
    def test_showcase_admin_add_no_user(self):
        """
        Calling showcase admin add with no user raises NotAuthorized.
        """

        context = {"user": None, "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_admin_add", context=context,
            )

    def test_showcase_admin_add_correct_creds(self):
        """
        Calling showcase admin add by a sysadmin doesn't raise
        NotAuthorized.
        """
        a_sysadmin = factories.Sysadmin()
        context = {"user": a_sysadmin["name"], "model": None}
        helpers.call_auth("ckanext_showcase_admin_add", context=context)

    def test_showcase_admin_add_unauthorized_creds(self):
        """
        Calling showcase admin add with unauthorized user raises
        NotAuthorized.
        """
        not_a_sysadmin = factories.User()
        context = {"user": not_a_sysadmin["name"], "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_admin_add", context=context,
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAdminRemoveAuth(object):
    def test_showcase_admin_remove_no_user(self):
        """
        Calling showcase admin remove with no user raises NotAuthorized.
        """

        context = {"user": None, "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_admin_remove", context=context,
            )

    def test_showcase_admin_remove_correct_creds(self):
        """
        Calling showcase admin remove by a sysadmin doesn't raise
        NotAuthorized.
        """
        a_sysadmin = factories.Sysadmin()
        context = {"user": a_sysadmin["name"], "model": None}
        helpers.call_auth("ckanext_showcase_admin_remove", context=context)

    def test_showcase_admin_remove_unauthorized_creds(self):
        """
        Calling showcase admin remove with unauthorized user raises
        NotAuthorized.
        """
        not_a_sysadmin = factories.User()
        context = {"user": not_a_sysadmin["name"], "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_admin_remove", context=context,
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAdminListAuth(object):
    def test_showcase_admin_list_no_user(self):
        """
        Calling showcase admin list with no user raises NotAuthorized.
        """

        context = {"user": None, "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_admin_list", context=context,
            )

    def test_showcase_admin_list_correct_creds(self):
        """
        Calling showcase admin list by a sysadmin doesn't raise
        NotAuthorized.
        """
        a_sysadmin = factories.Sysadmin()
        context = {"user": a_sysadmin["name"], "model": None}
        helpers.call_auth("ckanext_showcase_admin_list", context=context)

    def test_showcase_admin_list_unauthorized_creds(self):
        """
        Calling showcase admin list with unauthorized user raises
        NotAuthorized.
        """
        not_a_sysadmin = factories.User()
        context = {"user": not_a_sysadmin["name"], "model": None}
        with pytest.raises(toolkit.NotAuthorized):
            helpers.call_auth(
                "ckanext_showcase_admin_list", context=context,
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAuthManageShowcaseAdmins(object):
    def test_auth_anon_user_cant_view_showcase_admin_manage_page(self, app):
        """
        An anon (not logged in) user can't access the manage showcase admin
        page.
        """

        _get_request(app, "/showcase/new", status=302)

    def test_auth_logged_in_user_cant_view_showcase_admin_manage_page(
        self, app
    ):
        """
        A logged in user can't access the manage showcase admin page.
        """

        user = factories.User()
        app.get(
            "/showcase/new",
            status=401,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )

    def test_auth_sysadmin_can_view_showcase_admin_manage_page(self, app):
        """
        A sysadmin can access the manage showcase admin page.
        """

        user = factories.Sysadmin()
        app.get(
            "/showcase/new",
            status=200,
            extra_environ={"REMOTE_USER": str(user["name"])},
        )
