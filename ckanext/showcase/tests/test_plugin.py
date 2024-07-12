import pytest
from bs4 import BeautifulSoup

from ckan.lib.helpers import url_for


from ckan.plugins import toolkit as tk
import ckan.model as model

from ckan.tests import factories, helpers

from ckanext.showcase.model import ShowcasePackageAssociation

import logging

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestShowcaseIndex(object):
    def test_showcase_listed_on_index(self, app):
        """
        An added Showcase will appear on the Showcase index page.
        """

        factories.Dataset(type="showcase", name="my-showcase")

        response = app.get("/showcase", status=200)
        assert "1 showcase found" in response.body
        assert "my-showcase" in response.body


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestShowcaseNewView(object):
    def test_showcase_create_form_renders(self, app):

        sysadmin = factories.Sysadmin()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(url=url_for("showcase_new"), extra_environ=env,)
        assert "dataset-edit" in response

    def test_showcase_new_redirects_to_manage_datasets(self, app):
        """Creating a new showcase redirects to the manage datasets form."""
        sysadmin = factories.Sysadmin()
        # need a dataset for the 'bulk_action.showcase_add' button to show
        factories.Dataset()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.post(
            url=url_for("showcase_blueprint.new"),
            extra_environ=env,
            data={"name": "my-showcase"},
            follow_redirects=False
            )

        # Requested page is the manage_datasets url.
        assert (
            url_for("showcase_blueprint.manage_datasets", id="my-showcase")
            in response.location
        )

    def test_create_showcase(self, app):
        sysadmin = factories.Sysadmin()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        app.post(
            url=url_for("showcase_blueprint.new"),
            extra_environ=env,
            data={
                "name": "my-test-showcase",
                "image_url": "",
                "notes": "My new description!"
                }
            )

        res = app.get(
            url=url_for("showcase_blueprint.read", id="my-test-showcase"),
            extra_environ=env,
        )
        assert "my-test-showcase" in res.body
        assert "My new description!" in res.body



@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestShowcaseEditView(object):
    def test_showcase_edit_form_renders(self, app):
        """
        Edit form renders in response for ShowcaseController edit action.
        """

        sysadmin = factories.Sysadmin()
        factories.Dataset(name="my-showcase", type="showcase")

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("showcase_edit", id="my-showcase"), extra_environ=env,
        )
        assert "dataset-edit" in response

    def test_showcase_edit_redirects_to_showcase_details(self, app):
        """Editing a showcase redirects to the showcase details page."""
        if tk.check_ckan_version("2.9"):
            pytest.skip("submit_and_follow not supported")

        sysadmin = factories.Sysadmin()
        factories.Dataset(name="my-showcase", type="showcase")

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("showcase_edit", id="my-showcase"), extra_environ=env,
        )

        # edit showcase
        form = response.forms["dataset-edit"]
        form["name"] = u"my-changed-showcase"
        edit_response = helpers.submit_and_follow(app, form, env, "save")

        # Requested page is the showcase read url.
        assert (
            url_for("showcase_read", id="my-changed-showcase")
            == edit_response.request.path
        )

    def test_edit_showcase(self, app):
        sysadmin = factories.Sysadmin()
        factories.Dataset(name="my-showcase", type="showcase")
        env = {"REMOTE_USER": sysadmin["name"]}

        app.post(
            url=url_for("showcase_blueprint.edit", id="my-showcase"),
            extra_environ=env,
            data={
                "name": "my-edited-showcase",
                "notes": "My new description!",
                "image_url": ""
            }
        )
        res = app.get(
            url=url_for("showcase_blueprint.edit", id="my-edited-showcase"),
            extra_environ=env,
        )
        assert "my-edited-showcase" in res.body
        assert "My new description!" in res.body


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetView(object):

    """Plugin adds a new showcases view for datasets."""

    def test_dataset_read_has_showcases_tab(self, app):
        """
        Dataset view page has a new Showcases tab linked to the correct place.
        """

        dataset = factories.Dataset(name="my-dataset")

        url = url = url_for("dataset.read", id=dataset["id"])

        response = app.get(url)
        # response contains link to dataset's showcase list
        assert "/dataset/showcases/{0}".format(dataset["name"]) in response

    def test_dataset_showcase_page_lists_showcases_no_associations(self, app):
        """
        No showcases are listed if dataset has no showcase associations.
        """

        dataset = factories.Dataset(name="my-dataset")

        response = app.get(
            url=url_for("showcase_blueprint.dataset_showcase_list", id=dataset["id"])
        )

        assert (
            len(
                BeautifulSoup(response.body).select(
                    "ul.media-grid li.media-item"
                )
            )
            == 0
        )

    def test_dataset_showcase_page_lists_showcases_two_associations(self, app):
        """
        Two showcases are listed for dataset with two showcase associations.
        """

        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name="my-dataset")
        showcase_one = factories.Dataset(
            name="my-first-showcase", type="showcase"
        )
        showcase_two = factories.Dataset(
            name="my-second-showcase", type="showcase"
        )
        factories.Dataset(name="my-third-showcase", type="showcase")

        context = {"user": sysadmin["name"]}
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=dataset["id"],
            showcase_id=showcase_one["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=dataset["id"],
            showcase_id=showcase_two["id"],
        )

        response = app.get(
            url=url_for("showcase_blueprint.dataset_showcase_list", id=dataset["id"])
        )

        assert len(BeautifulSoup(response.body).select("li.media-item")) == 2
        assert "my-first-showcase" in response
        assert "my-second-showcase" in response
        assert "my-third-showcase" not in response

    def test_dataset_showcase_page_add_to_showcase_dropdown_list(self, app):
        """
        Add to showcase dropdown only lists showcases that aren't already
        associated with dataset.
        """
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name="my-dataset")
        showcase_one = factories.Dataset(
            name="my-first-showcase", type="showcase"
        )
        showcase_two = factories.Dataset(
            name="my-second-showcase", type="showcase"
        )
        showcase_three = factories.Dataset(
            name="my-third-showcase", type="showcase"
        )

        context = {"user": sysadmin["name"]}
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=dataset["id"],
            showcase_id=showcase_one["id"],
        )

        response = app.get(
            url=url_for("showcase_blueprint.dataset_showcase_list", id=dataset["id"]),
            extra_environ={"REMOTE_USER": str(sysadmin["name"])},
        )

        assert f'<option value="{showcase_one["id"]}' not in response.body
        assert f'<option value="{showcase_two["id"]}' in response.body
        assert f'<option value="{showcase_three["id"]}' in response.body

    def test_dataset_showcase_page_add_showcase_button_submit(self, app):
        """
        Submitting 'Add to showcase' form with selected showcase value creates
        a sc/pkg association.
        """

        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name="my-dataset")
        showcase_one = factories.Dataset(
            name="my-first-showcase", type="showcase"
        )
        factories.Dataset(name="my-second-showcase", type="showcase")
        factories.Dataset(name="my-third-showcase", type="showcase")

        assert model.Session.query(ShowcasePackageAssociation).count() == 0

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}

        response = app.post(
            url=url_for("showcase_blueprint.dataset_showcase_list", id=dataset["id"]),
            data={"showcase_added": showcase_one["id"]},
            extra_environ=env,
        )

        # Flash message containing confirmation
        assert "The dataset has been added to the showcase" in response.body

        # an association is created
        assert model.Session.query(ShowcasePackageAssociation).count() == 1

    def test_dataset_showcase_page_remove_showcase_button_submit(self, app):
        """
        Submitting 'Remove' form with selected showcase value deletes a sc/pkg
        association.
        """

        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name="my-dataset")
        showcase_one = factories.Dataset(
            name="my-first-showcase", type="showcase"
        )

        context = {"user": sysadmin["name"]}
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=dataset["id"],
            showcase_id=showcase_one["id"],
        )

        assert model.Session.query(ShowcasePackageAssociation).count() == 1

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}

        response = app.post(
            url=url_for("showcase_blueprint.dataset_showcase_list", id=dataset["id"]),
            data={"remove_showcase_id": showcase_one["id"]},
            extra_environ=env,
        )

        # Flash message containing confirmation
        assert "The dataset has been removed from the showcase." in response.body

        # the association is deleted
        assert model.Session.query(ShowcasePackageAssociation).count() == 0


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestShowcaseAdminManageView(object):

    """Plugin adds a showcase admin management page to ckan-admin section."""

    def test_ckan_admin_has_showcase_config_tab(self, app):
        """
        ckan-admin index page has a showcase config tab.
        """
        sysadmin = factories.Sysadmin()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("admin.index"), extra_environ=env
        )
        # response contains link to dataset's showcase list
        assert "/ckan-admin/showcase_admins" in response

    def test_showcase_admin_manage_page_returns_correct_status(self, app):
        """
        /ckan-admin/showcase_admins can be successfully accessed.
        """

        sysadmin = factories.Sysadmin()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        app.get(url=url_for("showcase_blueprint.admins"), status=200, extra_environ=env)

    def test_showcase_admin_manage_page_lists_showcase_admins(self, app):
        """
        Showcase admins are listed on the showcase admin page.
        """

        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action(
            "ckanext_showcase_admin_add", context={}, username=user_one["name"]
        )
        helpers.call_action(
            "ckanext_showcase_admin_add", context={}, username=user_two["name"]
        )

        sysadmin = factories.Sysadmin()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("showcase_blueprint.admins"), status=200, extra_environ=env
        )

        assert "/user/{0}".format(user_one["name"]) in response
        assert "/user/{0}".format(user_two["name"]) in response
        assert "/user/{0}".format(user_three["name"]) not in response

    def test_showcase_admin_manage_page_no_admins_message(self, app):
        """
        Showcase admins page displays message if no showcase admins present.
        """

        sysadmin = factories.Sysadmin()

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("showcase_blueprint.admins"), status=200, extra_environ=env
        )

        assert "There are currently no Showcase Admins" in response


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestSearch(object):
    def test_search_with_nonascii_filter_query(self, app):
        """
        Searching with non-ASCII filter queries works.

        See https://github.com/ckan/ckanext-showcase/issues/34.
        """

        tag = u"\xe4\xf6\xfc"
        factories.Dataset(tags=[{"name": tag, "state": "active"}])
        result = helpers.call_action("package_search", fq="tags:" + tag)
        assert result["count"] == 1


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCKEditor(object):
    @pytest.mark.ckan_config("ckanext.showcase.editor", "ckeditor")
    def test_rich_text_editor_is_shown_when_configured(self, app):

        sysadmin = factories.Sysadmin()
        factories.Dataset(name="my-showcase", type="showcase")

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("showcase_edit", id="my-showcase",), extra_environ=env,
        )
        assert '<textarea id="editor"' in response.body

    def test_rich_text_editor_is_not_shown_when_not_configured(self, app):

        sysadmin = factories.Sysadmin()
        factories.Dataset(name="my-showcase", type="showcase")

        env = {"REMOTE_USER": sysadmin["name"].encode("ascii")}
        response = app.get(
            url=url_for("showcase_blueprint.edit", id="my-showcase",), extra_environ=env,
        )
        assert '<textarea id="editor"' not in response.body

    @pytest.mark.ckan_config("ckanext.showcase.editor", "ckeditor")
    def test_custom_div_content_is_used_with_ckeditor(self, app):
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-showcase', type='showcase')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for("showcase_blueprint.read", id="my-showcase",), extra_environ=env,
        )
        assert '<div class="ck-content">' in response.body
