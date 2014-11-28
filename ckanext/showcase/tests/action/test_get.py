from nose import tools as nosetools

import ckan.plugins.toolkit as toolkit
import ckan.new_tests.factories as factories
import ckan.new_tests.helpers as helpers


class TestShowcasePackageList(helpers.FunctionalTestBase):

    def test_showcase_package_list_no_packages(self):
        '''
        Calling ckanext_showcase_package_list with a showcase that has no
        packages returns an empty list.
        '''
        showcase_id = factories.Dataset(type='showcase')['id']

        pkg_list = helpers.call_action('ckanext_showcase_package_list',
                                       showcase_id=showcase_id)

        nosetools.assert_equal(pkg_list, [])

    def test_showcase_package_list_works_with_name(self):
        '''
        Calling ckanext_showcase_package_list with a showcase name doesn't
        raise a ValidationError.
        '''
        showcase_name = factories.Dataset(type='showcase')['name']

        pkg_list = helpers.call_action('ckanext_showcase_package_list',
                                       showcase_id=showcase_name)

        nosetools.assert_equal(pkg_list, [])

    def test_showcase_package_list_wrong_showcase_id(self):
        '''
        Calling ckanext_showcase_package_list with a bad showcase id raises a
        ValidationError.
        '''
        factories.Dataset(type='showcase')['id']

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_list',
                                showcase_id='a-bad-id')

    def test_showcase_package_list_showcase_has_package(self):
        '''
        Calling ckanext_showcase_package_list with a showcase that has a
        package should return that package.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        showcase_id = factories.Dataset(type='showcase')['id']
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=package['id'],
                            showcase_id=showcase_id)

        pkg_list = helpers.call_action('ckanext_showcase_package_list',
                                       showcase_id=showcase_id)

        # We've got an item in the pkg_list
        nosetools.assert_equal(len(pkg_list), 1)
        # The list item should have the correct name property
        nosetools.assert_equal(pkg_list[0]['name'], package['name'])

    def test_showcase_package_list_showcase_has_two_packages(self):
        '''
        Calling ckanext_showcase_package_list with a showcase that has two
        packages should return the packages.
        '''
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        showcase_id = factories.Dataset(type='showcase')['id']
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=package_one['id'],
                            showcase_id=showcase_id)
        # create second association
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=package_two['id'],
                            showcase_id=showcase_id)

        pkg_list = helpers.call_action('ckanext_showcase_package_list',
                                       showcase_id=showcase_id)

        # We've got two items in the pkg_list
        nosetools.assert_equal(len(pkg_list), 2)
