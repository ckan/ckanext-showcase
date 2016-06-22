from nose import tools as nosetools

from ckan.model.package import Package
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


class TestCreateShowcase(ShowcaseFunctionalTestBase):

    def test_showcase_create_no_args(self):
        '''
        Calling showcase create without args raises ValidationError.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}

        # no showcases exist.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 0)

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_create',
                                context=context)

        # no showcases (dataset of type 'showcase') created.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 0)

    def test_showcase_create_with_name_arg(self):
        '''
        Calling showcase create with a name arg creates a showcase package.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}

        # no showcases exist.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 0)

        helpers.call_action('ckanext_showcase_create',
                            context=context, name='my-showcase')

        # a showcases (dataset of type 'showcase') created.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 1)

    def test_showcase_create_with_existing_name(self):
        '''
        Calling showcase create with an existing name raises ValidationError.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        factories.Dataset(type='showcase', name='my-showcase')

        # a single showcases exist.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 1)

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_create',
                                context=context, name='my-showcase')

        # still only one showcase exists.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'showcase').count(), 1)


class TestCreateShowcasePackageAssociation(ShowcaseFunctionalTestBase):

    def test_association_create_no_args(self):
        '''
        Calling sc/pkg association create with no args raises
        ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_create',
                                context=context)

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)

    def test_association_create_missing_arg(self):
        '''
        Calling sc/pkg association create with a missing arg raises
        ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']

        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_create',
                                context=context, package_id=package_id)

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)

    def test_association_create_by_id(self):
        '''
        Calling sc/pkg association create with correct args (package ids)
        creates an association.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        showcase_id = factories.Dataset(type='showcase')['id']

        context = {'user': sysadmin['name']}
        association_dict = helpers.call_action('ckanext_showcase_package_association_create',
                                               context=context, package_id=package_id,
                                               showcase_id=showcase_id)

        # One association object created
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 1)
        # Association properties are correct
        nosetools.assert_equal(association_dict.get('showcase_id'), showcase_id)
        nosetools.assert_equal(association_dict.get('package_id'), package_id)

    def test_association_create_by_name(self):
        '''
        Calling sc/pkg association create with correct args (package names)
        creates an association.
        '''
        sysadmin = factories.User(sysadmin=True)
        package = factories.Dataset()
        package_name = package['name']
        showcase = factories.Dataset(type='showcase')
        showcase_name = showcase['name']

        context = {'user': sysadmin['name']}
        association_dict = helpers.call_action('ckanext_showcase_package_association_create',
                                               context=context, package_id=package_name,
                                               showcase_id=showcase_name)

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 1)
        nosetools.assert_equal(association_dict.get('showcase_id'), showcase['id'])
        nosetools.assert_equal(association_dict.get('package_id'), package['id'])

    def test_association_create_existing(self):
        '''
        Attempt to create association with existing details returns Validation
        Error.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        showcase_id = factories.Dataset(type='showcase')['id']

        context = {'user': sysadmin['name']}
        # Create association
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=package_id,
                            showcase_id=showcase_id)
        # Attempted duplicate creation results in ValidationError
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_package_association_create',
                                context=context, package_id=package_id,
                                showcase_id=showcase_id)


class TestCreateShowcaseAdmin(ShowcaseFunctionalTestBase):

    def test_showcase_admin_add_creates_showcase_admin_user(self):
        '''
        Calling ckanext_showcase_admin_add adds user to showcase admin list.
        '''
        user_to_add = factories.User()

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 0)

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user_to_add['name'])

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 1)
        nosetools.assert_true(user_to_add['id'] in ShowcaseAdmin.get_showcase_admin_ids())

    def test_showcase_admin_add_multiple_users(self):
        '''
        Calling ckanext_showcase_admin_add for multiple users correctly adds
        them to showcase admin list.
        '''
        user_to_add = factories.User()
        second_user_to_add = factories.User()

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 0)

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user_to_add['name'])

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=second_user_to_add['name'])

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 2)
        nosetools.assert_true(user_to_add['id'] in ShowcaseAdmin.get_showcase_admin_ids())
        nosetools.assert_true(second_user_to_add['id'] in ShowcaseAdmin.get_showcase_admin_ids())

    def test_showcase_admin_add_existing_user(self):
        '''
        Calling ckanext_showcase_admin_add twice for same user raises a
        ValidationError.
        '''
        user_to_add = factories.User()

        # Add once
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user_to_add['name'])

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 1)

        # Attempt second add
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_admin_add', context={},
                                username=user_to_add['name'])

        # Still only one ShowcaseAdmin object.
        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 1)

    def test_showcase_admin_add_username_doesnot_exist(self):
        '''
        Calling ckanext_showcase_admin_add with non-existent username raises
        ValidationError and no ShowcaseAdmin object is created.
        '''
        nosetools.assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                                'ckanext_showcase_admin_add', context={},
                                username='missing')

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 0)
        nosetools.assert_equal(ShowcaseAdmin.get_showcase_admin_ids(), [])

    def test_showcase_admin_add_no_args(self):
        '''
        Calling ckanext_showcase_admin_add with no args raises ValidationError
        and no ShowcaseAdmin object is created.
        '''
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_showcase_admin_add', context={})

        nosetools.assert_equal(model.Session.query(ShowcaseAdmin).count(), 0)
        nosetools.assert_equal(ShowcaseAdmin.get_showcase_admin_ids(), [])
