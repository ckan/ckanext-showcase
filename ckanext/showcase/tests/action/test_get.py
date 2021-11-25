# -*- coding: utf-8 -*-

import pytest

from ckan.tests import factories, helpers
import ckan.plugins.toolkit as toolkit


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseShow(object):
    def test_showcase_show_no_args(self):
        """
        Calling showcase show with no args raises a ValidationError.
        """
        with pytest.raises(toolkit.ValidationError):
            helpers.call_action("ckanext_showcase_show")

    def test_showcase_show_with_id(self):
        """
        Calling showcase show with id arg returns showcase dict.
        """
        my_showcase = factories.Dataset(type="showcase", name="my-showcase")

        showcase_shown = helpers.call_action(
            "ckanext_showcase_show", id=my_showcase["id"]
        )

        assert my_showcase["name"] == showcase_shown["name"]

    def test_showcase_show_with_name(self):
        """
        Calling showcase show with name arg returns showcase dict.
        """
        my_showcase = factories.Dataset(type="showcase", name="my-showcase")

        showcase_shown = helpers.call_action(
            "ckanext_showcase_show", id=my_showcase["name"]
        )

        assert my_showcase["id"] == showcase_shown["id"]

    def test_showcase_show_with_nonexisting_name(self):
        """
        Calling showcase show with bad name arg returns ObjectNotFound.
        """
        factories.Dataset(type="showcase", name="my-showcase")

        with pytest.raises(toolkit.ObjectNotFound):
            helpers.call_action(
                "ckanext_showcase_show", id="my-bad-name",
            )

    def test_showcase_show_num_datasets_added(self):
        """
        num_datasets property returned with showcase dict.
        """
        my_showcase = factories.Dataset(type="showcase", name="my-showcase")

        showcase_shown = helpers.call_action(
            "ckanext_showcase_show", id=my_showcase["name"]
        )

        assert "num_datasets" in showcase_shown
        assert showcase_shown["num_datasets"] == 0

    def test_showcase_show_num_datasets_correct_value(self):
        """
        num_datasets property has correct value.
        """

        sysadmin = factories.User(sysadmin=True)

        my_showcase = factories.Dataset(type="showcase", name="my-showcase")
        package_one = factories.Dataset()
        package_two = factories.Dataset()

        context = {"user": sysadmin["name"]}
        # create an association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_one["id"],
            showcase_id=my_showcase["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_two["id"],
            showcase_id=my_showcase["id"],
        )

        showcase_shown = helpers.call_action(
            "ckanext_showcase_show", id=my_showcase["name"]
        )

        assert showcase_shown["num_datasets"] == 2

    def test_showcase_show_num_datasets_correct_only_count_active_datasets(
        self,
    ):
        """
        num_datasets property has correct value when some previously
        associated datasets have been datasets.
        """
        sysadmin = factories.User(sysadmin=True)

        my_showcase = factories.Dataset(type="showcase", name="my-showcase")
        package_one = factories.Dataset()
        package_two = factories.Dataset()
        package_three = factories.Dataset()

        context = {"user": sysadmin["name"]}
        # create the associations
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_one["id"],
            showcase_id=my_showcase["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_two["id"],
            showcase_id=my_showcase["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_three["id"],
            showcase_id=my_showcase["id"],
        )

        # delete the first package
        helpers.call_action(
            "package_delete", context=context, id=package_one["id"]
        )

        showcase_shown = helpers.call_action(
            "ckanext_showcase_show", id=my_showcase["name"]
        )

        # the num_datasets should only include active datasets
        assert showcase_shown["num_datasets"] == 2

    def test_showcase_anon_user_can_see_package_list_when_showcase_association_was_deleted(
        self, app
    ):
        """
        When a showcase is deleted, the remaining associations with formerly associated
        packages or showcases can still be displayed.
        """

        sysadmin = factories.User(sysadmin=True)

        showcase_one = factories.Dataset(type="showcase", name="showcase-one")
        showcase_two = factories.Dataset(type="showcase", name="showcase-two")
        package_one = factories.Dataset()
        package_two = factories.Dataset()

        admin_context = {"user": sysadmin["name"]}

        # create the associations
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=admin_context,
            package_id=package_one["id"],
            showcase_id=showcase_one["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=admin_context,
            package_id=package_one["id"],
            showcase_id=showcase_two["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=admin_context,
            package_id=package_two["id"],
            showcase_id=showcase_one["id"],
        )
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=admin_context,
            package_id=package_two["id"],
            showcase_id=showcase_two["id"],
        )

        # delete one of the associated showcases
        helpers.call_action(
            "package_delete", context=admin_context, id=showcase_two["id"]
        )

        # the anon user can still see the associated packages of remaining showcase
        associated_packages = helpers.call_action(
            "ckanext_showcase_package_list", showcase_id=showcase_one["id"]
        )

        assert len(associated_packages) == 2

        # overview of packages can still be seen
        app.get("/dataset", status=200)


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseList(object):
    def test_showcase_list(self):
        """Showcase list action returns names of showcases in site."""

        showcase_one = factories.Dataset(type="showcase")
        showcase_two = factories.Dataset(type="showcase")
        showcase_three = factories.Dataset(type="showcase")

        showcase_list = helpers.call_action("ckanext_showcase_list")

        showcase_list_name_id = [
            (sc["name"], sc["id"]) for sc in showcase_list
        ]

        assert len(showcase_list) == 3
        assert sorted(showcase_list_name_id) == sorted(
            [
                (showcase["name"], showcase["id"])
                for showcase in [showcase_one, showcase_two, showcase_three,]
            ]
        )

    def test_showcase_list_no_datasets(self):
        """
        Showcase list action doesn't return normal datasets (of type
        'dataset').
        """
        showcase_one = factories.Dataset(type="showcase")
        dataset_one = factories.Dataset()
        dataset_two = factories.Dataset()

        showcase_list = helpers.call_action("ckanext_showcase_list")

        showcase_list_name_id = [
            (sc["name"], sc["id"]) for sc in showcase_list
        ]

        assert len(showcase_list) == 1
        assert (
            showcase_one["name"],
            showcase_one["id"],
        ) in showcase_list_name_id
        assert (
            dataset_one["name"],
            dataset_one["id"],
        ) not in showcase_list_name_id
        assert (
            dataset_two["name"],
            dataset_two["id"],
        ) not in showcase_list_name_id


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcasePackageList(object):

    """Tests for ckanext_showcase_package_list"""

    def test_showcase_package_list_no_packages(self):
        """
        Calling ckanext_showcase_package_list with a showcase that has no
        packages returns an empty list.
        """
        showcase_id = factories.Dataset(type="showcase")["id"]

        pkg_list = helpers.call_action(
            "ckanext_showcase_package_list", showcase_id=showcase_id
        )

        assert pkg_list == []

    def test_showcase_package_list_works_with_name(self):
        """
        Calling ckanext_showcase_package_list with a showcase name doesn't
        raise a ValidationError.
        """
        showcase_name = factories.Dataset(type="showcase")["name"]

        pkg_list = helpers.call_action(
            "ckanext_showcase_package_list", showcase_id=showcase_name
        )

        assert pkg_list == []

    def test_showcase_package_list_wrong_showcase_id(self):
        """
        Calling ckanext_showcase_package_list with a bad showcase id raises a
        ValidationError.
        """
        factories.Dataset(type="showcase")["id"]

        with pytest.raises(toolkit.ValidationError):
            helpers.call_action(
                "ckanext_showcase_package_list", showcase_id="a-bad-id",
            )

    def test_showcase_package_list_showcase_has_package(self):
        """
        Calling ckanext_showcase_package_list with a showcase that has a
        package should return that package.
        """
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        showcase_id = factories.Dataset(type="showcase")["id"]
        context = {"user": sysadmin["name"]}
        # create an association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package["id"],
            showcase_id=showcase_id,
        )

        pkg_list = helpers.call_action(
            "ckanext_showcase_package_list", showcase_id=showcase_id
        )

        # We've got an item in the pkg_list
        assert len(pkg_list) == 1
        # The list item should have the correct name property
        assert pkg_list[0]["name"] == package["name"]

    def test_showcase_package_list_showcase_has_two_packages(self):
        """
        Calling ckanext_showcase_package_list with a showcase that has two
        packages should return the packages.
        """
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        showcase_id = factories.Dataset(type="showcase")["id"]
        context = {"user": sysadmin["name"]}
        # create first association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_one["id"],
            showcase_id=showcase_id,
        )
        # create second association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_two["id"],
            showcase_id=showcase_id,
        )

        pkg_list = helpers.call_action(
            "ckanext_showcase_package_list", showcase_id=showcase_id
        )

        # We've got two items in the pkg_list
        assert len(pkg_list) == 2

    def test_showcase_package_list_showcase_only_contains_active_datasets(
        self,
    ):
        """
        Calling ckanext_showcase_package_list will only return active datasets
        (not deleted ones).
        """
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        package_three = factories.Dataset()
        showcase_id = factories.Dataset(type="showcase")["id"]
        context = {"user": sysadmin["name"]}
        # create first association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_one["id"],
            showcase_id=showcase_id,
        )
        # create second association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_two["id"],
            showcase_id=showcase_id,
        )
        # create third association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package_three["id"],
            showcase_id=showcase_id,
        )

        # delete the first package
        helpers.call_action(
            "package_delete", context=context, id=package_one["id"]
        )

        pkg_list = helpers.call_action(
            "ckanext_showcase_package_list", showcase_id=showcase_id
        )

        # We've got two items in the pkg_list
        assert len(pkg_list) == 2

        pkg_list_ids = [pkg["id"] for pkg in pkg_list]
        assert package_two["id"] in pkg_list_ids
        assert package_three["id"] in pkg_list_ids
        assert package_one["id"] not in pkg_list_ids

    def test_showcase_package_list_package_isnot_a_showcase(self):
        """
        Calling ckanext_showcase_package_list with a package id should raise a
        ValidationError.

        Since Showcases are Packages under the hood, make sure we treat them
        differently.
        """
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        showcase_id = factories.Dataset(type="showcase")["id"]
        context = {"user": sysadmin["name"]}
        # create an association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package["id"],
            showcase_id=showcase_id,
        )

        with pytest.raises(toolkit.ValidationError):
            helpers.call_action(
                "ckanext_showcase_package_list", showcase_id=package["id"],
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestPackageShowcaseList(object):

    """Tests for ckanext_package_showcase_list"""

    def test_package_showcase_list_no_showcases(self):
        """
        Calling ckanext_package_showcase_list with a package that has no
        showcases returns an empty list.
        """
        package_id = factories.Dataset()["id"]

        showcase_list = helpers.call_action(
            "ckanext_package_showcase_list", package_id=package_id
        )

        assert showcase_list == []

    def test_package_showcase_list_works_with_name(self):
        """
        Calling ckanext_package_showcase_list with a package name doesn't
        raise a ValidationError.
        """
        package_name = factories.Dataset()["name"]

        showcase_list = helpers.call_action(
            "ckanext_package_showcase_list", package_id=package_name
        )

        assert showcase_list == []

    def test_package_showcase_list_wrong_showcase_id(self):
        """
        Calling ckanext_package_showcase_list with a bad package id raises a
        ValidationError.
        """
        factories.Dataset()["id"]

        with pytest.raises(toolkit.ValidationError):
            helpers.call_action(
                "ckanext_package_showcase_list", showcase_id="a-bad-id",
            )

    def test_package_showcase_list_showcase_has_package(self):
        """
        Calling ckanext_package_showcase_list with a package that has a
        showcase should return that showcase.
        """
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        showcase = factories.Dataset(type="showcase")
        context = {"user": sysadmin["name"]}
        # create an association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package["id"],
            showcase_id=showcase["id"],
        )

        showcase_list = helpers.call_action(
            "ckanext_package_showcase_list", package_id=package["id"]
        )

        # We've got an item in the showcase_list
        assert len(showcase_list) == 1
        # The list item should have the correct name property
        assert showcase_list[0]["name"] == showcase["name"]

    def test_package_showcase_list_showcase_has_two_packages(self):
        """
        Calling ckanext_package_showcase_list with a package that has two
        showcases should return the showcases.
        """
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        showcase_one = factories.Dataset(type="showcase")
        showcase_two = factories.Dataset(type="showcase")
        context = {"user": sysadmin["name"]}
        # create first association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package["id"],
            showcase_id=showcase_one["id"],
        )
        # create second association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package["id"],
            showcase_id=showcase_two["id"],
        )

        showcase_list = helpers.call_action(
            "ckanext_package_showcase_list", package_id=package["id"]
        )

        # We've got two items in the showcase_list
        assert len(showcase_list) == 2

    def test_package_showcase_list_package_isnot_a_showcase(self):
        """
        Calling ckanext_package_showcase_list with a showcase id should raise a
        ValidationError.

        Since Showcases are Packages under the hood, make sure we treat them
        differently.
        """
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        showcase = factories.Dataset(type="showcase")
        context = {"user": sysadmin["name"]}
        # create an association
        helpers.call_action(
            "ckanext_showcase_package_association_create",
            context=context,
            package_id=package["id"],
            showcase_id=showcase["id"],
        )

        with pytest.raises(toolkit.ValidationError):
            helpers.call_action(
                "ckanext_package_showcase_list", package_id=showcase["id"],
            )


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestShowcaseAdminList(object):

    """Tests for ckanext_showcase_admin_list"""

    def test_showcase_admin_list_no_showcase_admins(self):
        """
        Calling ckanext_showcase_admin_list on a site that has no showcases
        admins returns an empty list.
        """

        showcase_admin_list = helpers.call_action(
            "ckanext_showcase_admin_list"
        )

        assert showcase_admin_list == []

    def test_showcase_admin_list_users(self):
        """
        Calling ckanext_showcase_admin_list will return users who are showcase
        admins.
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
        helpers.call_action(
            "ckanext_showcase_admin_add",
            context={},
            username=user_three["name"],
        )

        showcase_admin_list = helpers.call_action(
            "ckanext_showcase_admin_list", context={}
        )

        assert len(showcase_admin_list) == 3
        for user in [user_one, user_two, user_three]:
            assert {
                "name": user["name"],
                "id": user["id"],
            } in showcase_admin_list

    def test_showcase_admin_only_lists_admin_users(self):
        """
        Calling ckanext_showcase_admin_list will only return users who are
        showcase admins.
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

        showcase_admin_list = helpers.call_action(
            "ckanext_showcase_admin_list", context={}
        )

        assert len(showcase_admin_list) == 2
        # user three isn't in list
        assert {
            "name": user_three["name"],
            "id": user_three["id"],
        } not in showcase_admin_list


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestPackageSearchBeforeSearch(object):

    """
    Extension uses the `before_search` method to alter search parameters.
    """

    def test_package_search_no_additional_filters(self):
        """
        Perform package_search with no additional filters should not include
        showcases.
        """
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type="showcase")
        factories.Dataset(type="custom")

        search_results = helpers.call_action("package_search", context={})[
            "results"
        ]

        types = [result["type"] for result in search_results]

        assert len(search_results) == 3
        assert "showcase" not in types
        assert "custom" in types

    def test_package_search_filter_include_showcase(self):
        """
        package_search filtered to include datasets of type showcase should
        only include showcases.
        """
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type="showcase")
        factories.Dataset(type="custom")

        search_results = helpers.call_action(
            "package_search", context={}, fq="dataset_type:showcase"
        )["results"]

        types = [result["type"] for result in search_results]

        assert len(search_results) == 1
        assert "showcase" in types
        assert "custom" not in types
        assert "dataset" not in types


@pytest.mark.usefixtures("clean_db", "clean_index")
class TestUserShowBeforeSearch(object):

    """
    Extension uses the `before_search` method to alter results of user_show
    (via package_search).
    """

    def test_user_show_no_additional_filters(self):
        """
        Perform package_search with no additional filters should not include
        showcases.
        """

        user = factories.User()
        factories.Dataset(user=user)
        factories.Dataset(user=user)
        factories.Dataset(user=user, type="showcase")
        factories.Dataset(user=user, type="custom")

        search_results = helpers.call_action(
            "user_show", context={}, include_datasets=True, id=user["name"]
        )["datasets"]

        types = [result["type"] for result in search_results]

        assert len(search_results) == 3
        assert "showcase" not in types
        assert "custom" in types
