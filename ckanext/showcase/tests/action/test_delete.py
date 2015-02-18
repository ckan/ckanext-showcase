from nose import tools as nosetools

import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.new_tests.factories as factories
import ckan.new_tests.helpers as helpers

from ckanext.showcase.model import ShowcasePackageAssociation
from ckan.model.package import Package


class TestDeleteShowcase(helpers.FunctionalTestBase):

    def test_showcase_delete_no_args(self):
        '''
        Calling showcase delete with no args raises a ValidationError.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_delete', context=context)

    def test_showcase_delete_incorrect_args(self):
        '''
        Calling showcase delete with incorrect args raises ObjectNotFound.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        factories.Dataset(type='showcase')
        nosetools.assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                                'ckanext_showcase_delete', context=context,
                                id='blah-blah')

    def test_showcase_delete_by_id(self):
        '''
        Calling showcase delete with showcase id.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        showcase = factories.Dataset(type='showcase')

        # One showcase object created
        nosetools.assert_equal(model.Session.query(Package).count(), 1)

        helpers.call_action('ckanext_showcase_delete',
                            context=context, id=showcase['id'])

        nosetools.assert_equal(model.Session.query(Package).count(), 0)

    def test_showcase_delete_by_name(self):
        '''
        Calling showcase delete with showcase name.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        showcase = factories.Dataset(type='showcase')

        # One showcase object created
        nosetools.assert_equal(model.Session.query(Package).count(), 1)

        helpers.call_action('ckanext_showcase_delete',
                            context=context, id=showcase['name'])

        nosetools.assert_equal(model.Session.query(Package).count(), 0)

    def test_showcase_delete_removes_associations(self):
        '''
        Deleting a showcase also deletes associated ShowcasePackageAssociation
        objects.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        showcase = factories.Dataset(type='showcase', name='my-showcase')
        dataset_one = factories.Dataset(name='dataset-one')
        dataset_two = factories.Dataset(name='dataset-two')

        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=dataset_one['id'],
                            showcase_id=showcase['id'])
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=dataset_two['id'],
                            showcase_id=showcase['id'])

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 2)

        helpers.call_action('ckanext_showcase_delete',
                            context=context, id=showcase['id'])

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)


class TestDeleteShowcasePackageAssociation(helpers.FunctionalTestBase):

    def test_association_delete_no_args(self):
        '''
        Calling sc/pkg association delete with no args raises ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_delete',
                                context=context)

    def test_association_delete_missing_arg(self):
        '''
        Calling sc/pkg association delete with a missing arg raises
        ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']

        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_delete',
                                context=context, package_id=package_id)

    def test_association_delete_by_id(self):
        '''
        Calling sc/pkg association delete with correct args (package ids)
        correctly deletes an association.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        showcase_id = factories.Dataset(type='showcase')['id']

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=package_id,
                            showcase_id=showcase_id)

        # One association object created
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 1)

        helpers.call_action('ckanext_showcase_package_association_delete',
                            context=context, package_id=package_id,
                            showcase_id=showcase_id)

    def test_association_delete_attempt_with_non_existent_association(self):
        '''
        Attempting to delete a non-existent association (package ids exist,
        but aren't associated with each other), will cause a ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        showcase_id = factories.Dataset(type='showcase')['id']

        # No existing associations
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)

        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_delete',
                                context=context, package_id=package_id,
                                showcase_id=showcase_id)

    def test_association_delete_attempt_with_bad_package_ids(self):
        '''
        Attempting to delete an association by passing non-existent package
        ids will cause a ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)

        # No existing associations
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)

        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_delete',
                                context=context, package_id="my-bad-package-id",
                                showcase_id="my-bad-showcase-id")

    def test_association_delete_retains_packages(self):
        '''
        Deleting a sc/pkg association doesn't delete the associated packages.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        showcase_id = factories.Dataset(type='showcase')['id']

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=package_id,
                            showcase_id=showcase_id)

        helpers.call_action('ckanext_showcase_package_association_delete',
                            context=context, package_id=package_id,
                            showcase_id=showcase_id)

        # packages still exist
        nosetools.assert_equal(model.Session.query(Package).count(), 2)
