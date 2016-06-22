from nose import tools as nosetools

import ckan.model as model
import ckan.plugins.toolkit as toolkit
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

from ckanext.showcase.model import ShowcasePackageAssociation, ShowcaseAdmin
from ckanext.showcase.tests import ShowcaseFunctionalTestBase
from ckan.model.package import Package


class TestDeleteShowcase(ShowcaseFunctionalTestBase):

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
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 1)

        helpers.call_action('ckanext_showcase_delete',
                            context=context, id=showcase['id'])

        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 0)

    def test_showcase_delete_by_name(self):
        '''
        Calling showcase delete with showcase name.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        showcase = factories.Dataset(type='showcase')

        # One showcase object created
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 1)

        helpers.call_action('ckanext_showcase_delete',
                            context=context, id=showcase['name'])

        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 0)

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


class TestDeletePackage(ShowcaseFunctionalTestBase):

    def test_package_delete_retains_associations(self):
        '''
        Deleting a package (setting its status to 'delete') retains associated
        ShowcasePackageAssociation objects.
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

        # delete the first package, should also delete the
        # ShowcasePackageAssociation associated with it.
        helpers.call_action('package_delete',
                            context=context, id=dataset_one['id'])

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 2)

    def test_package_purge_deletes_associations(self):
        '''
        Purging a package (actually deleting it from the database) deletes
        associated ShowcasePackageAssociation objects.
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

        # purge the first package, should also delete the
        # ShowcasePackageAssociation associated with it.
        pkg = model.Session.query(model.Package).get(dataset_one['id'])
        pkg.purge()
        model.repo.commit_and_remove()

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 1)


class TestDeleteShowcasePackageAssociation(ShowcaseFunctionalTestBase):

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
        but aren't associated with each other), will cause a NotFound error.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        showcase_id = factories.Dataset(type='showcase')['id']

        # No existing associations
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)

        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ObjectNotFound, helpers.call_action,
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

        # package still exist
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'dataset').count(), 1)

        # showcase still exist
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 1)


class TestRemoveShowcaseAdmin(ShowcaseFunctionalTestBase):

    def test_showcase_admin_remove_deletes_showcase_admin_user(self):
        '''
        Calling ckanext_showcase_admin_remove deletes ShowcaseAdmin object.
        '''
        user = factories.User()

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        # There's a ShowcaseAdmin obj
        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 1)

        helpers.call_action('ckanext_showcase_admin_remove', context={},
                            username=user['name'])

        # There's no ShowcaseAdmin obj
        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 0)
        nosetools.assert_equal(ShowcaseAdmin.get_showcase_admin_ids(), [])

    def test_showcase_admin_delete_user_removes_showcase_admin_object(self):
        '''
        Deleting a user also deletes the corresponding ShowcaseAdmin object.
        '''
        user = factories.User()

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        # There's a ShowcaseAdmin object
        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 1)
        nosetools.assert_true(user['id'] in ShowcaseAdmin.get_showcase_admin_ids())

        # purge the user, should also delete the ShowcaseAdmin object
        # associated with it.
        user_obj = model.Session.query(model.User).get(user['id'])
        user_obj.purge()
        model.repo.commit_and_remove()

        # The ShowcaseAdmin has also been removed
        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 0)
        nosetools.assert_equal(ShowcaseAdmin.get_showcase_admin_ids(), [])

    def test_showcase_admin_remove_retains_user(self):
        '''
        Deleting a ShowcaseAdmin object doesn't delete the corresponding user.
        '''

        user = factories.User()

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user['name'])

        # We have a user
        user_obj = model.Session.query(model.User).get(user['id'])
        nosetools.assert_true(user_obj is not None)

        helpers.call_action('ckanext_showcase_admin_remove', context={},
                            username=user['name'])

        # We still have a user
        user_obj = model.Session.query(model.User).get(user['id'])
        nosetools.assert_true(user_obj is not None)

    def test_showcase_admin_remove_with_bad_username(self):
        '''
        Calling showcase admin remove with a non-existent user raises
        ValidationError.
        '''

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_admin_remove', context={},
                                username='no-one-here')

    def test_showcase_admin_remove_with_no_args(self):
        '''
        Calling showcase admin remove with no arg raises ValidationError.
        '''

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_admin_remove', context={})
