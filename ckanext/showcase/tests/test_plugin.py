from routes import url_for
from nose import tools as nosetools
from nose import SkipTest

from ckan.plugins import toolkit as tk
import ckan.model as model
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

from ckanext.showcase.model import ShowcasePackageAssociation
from ckanext.showcase.tests import ShowcaseFunctionalTestBase

import logging
log = logging.getLogger(__name__)

submit_and_follow = helpers.submit_and_follow


class TestShowcaseIndex(ShowcaseFunctionalTestBase):

    def test_showcases_redirects_to_showcase(self):
        '''/showcases redirects to /showcase.'''
        app = self._get_test_app()
        response = app.get('/showcases', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/showcase')

    def test_showcases_redirects_to_showcase_for_item(self):
        '''/showcases/ redirects to /showcase.'''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get('/showcases/my-showcase', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/showcase/my-showcase')

    def test_showcase_listed_on_index(self):
        '''
        An added Showcase will appear on the Showcase index page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='showcase', name='my-showcase')

        response = app.get("/showcase", status=200)
        response.mustcontain("1 showcase found")
        response.mustcontain("my-showcase")


class TestShowcaseNewView(ShowcaseFunctionalTestBase):

    def test_showcase_create_form_renders(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController', action='new'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_showcase_new_redirects_to_manage_datasets(self):
        '''Creating a new showcase redirects to the manage datasets form.'''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        # need a dataset for the 'bulk_action.showcase_add' button to show
        factories.Dataset()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController', action='new'),
            extra_environ=env,
        )

        # create showcase
        form = response.forms['dataset-edit']
        form['name'] = u'my-showcase'
        create_response = submit_and_follow(app, form, env, 'save')

        # Unique to manage_datasets page
        nosetools.assert_true('bulk_action.showcase_add' in create_response)
        # Requested page is the manage_datasets url.
        nosetools.assert_equal(url_for(controller='ckanext.showcase.controller:ShowcaseController',
                                       action='manage_datasets', id='my-showcase'), create_response.request.path)


class TestShowcaseEditView(ShowcaseFunctionalTestBase):

    def test_showcase_edit_form_renders(self):
        '''
        Edit form renders in response for ShowcaseController edit action.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-showcase', type='showcase')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='edit',
                        id='my-showcase'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_showcase_edit_redirects_to_showcase_details(self):
        '''Editing a showcase redirects to the showcase details page.'''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-showcase', type='showcase')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='edit', id='my-showcase'),
            extra_environ=env,
        )

        # edit showcase
        form = response.forms['dataset-edit']
        form['name'] = u'my-changed-showcase'
        edit_response = submit_and_follow(app, form, env, 'save')

        # Requested page is the showcase read url.
        nosetools.assert_equal(url_for(controller='ckanext.showcase.controller:ShowcaseController',
                                       action='read', id='my-changed-showcase'), edit_response.request.path)


class TestDatasetView(ShowcaseFunctionalTestBase):

    '''Plugin adds a new showcases view for datasets.'''

    def test_dataset_read_has_showcases_tab(self):
        '''
        Dataset view page has a new Showcases tab linked to the correct place.
        '''
        app = self._get_test_app()
        dataset = factories.Dataset(name='my-dataset')

        response = app.get(
            url=url_for(controller='package', action='read', id=dataset['id'])
        )
        # response contains link to dataset's showcase list
        nosetools.assert_true('/dataset/showcases/{0}'.format(dataset['name']) in response)

    def test_dataset_showcase_page_lists_showcases_no_associations(self):
        '''
        No showcases are listed if dataset has no showcase associations.
        '''

        app = self._get_test_app()
        dataset = factories.Dataset(name='my-dataset')

        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='dataset_showcase_list', id=dataset['id'])
        )

        nosetools.assert_equal(len(response.html.select('ul.media-grid li.media-item')), 0)

    def test_dataset_showcase_page_lists_showcases_two_associations(self):
        '''
        Two showcases are listed for dataset with two showcase associations.
        '''

        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        showcase_one = factories.Dataset(name='my-first-showcase', type='showcase')
        showcase_two = factories.Dataset(name='my-second-showcase', type='showcase')
        factories.Dataset(name='my-third-showcase', type='showcase')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=dataset['id'],
                            showcase_id=showcase_one['id'])
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=dataset['id'],
                            showcase_id=showcase_two['id'])

        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='dataset_showcase_list', id=dataset['id'])
        )

        nosetools.assert_equal(len(response.html.select('li.media-item')), 2)
        nosetools.assert_true('my-first-showcase' in response)
        nosetools.assert_true('my-second-showcase' in response)
        nosetools.assert_true('my-third-showcase' not in response)

    def test_dataset_showcase_page_add_to_showcase_dropdown_list(self):
        '''
        Add to showcase dropdown only lists showcases that aren't already
        associated with dataset.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        showcase_one = factories.Dataset(name='my-first-showcase', type='showcase')
        showcase_two = factories.Dataset(name='my-second-showcase', type='showcase')
        showcase_three = factories.Dataset(name='my-third-showcase', type='showcase')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=dataset['id'],
                            showcase_id=showcase_one['id'])

        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='dataset_showcase_list', id=dataset['id']),
            extra_environ={'REMOTE_USER': str(sysadmin['name'])}
        )

        showcase_add_form = response.forms['showcase-add']
        showcase_added_options = [value for (value, _) in showcase_add_form['showcase_added'].options]
        nosetools.assert_true(showcase_one['id'] not in showcase_added_options)
        nosetools.assert_true(showcase_two['id'] in showcase_added_options)
        nosetools.assert_true(showcase_three['id'] in showcase_added_options)

    def test_dataset_showcase_page_add_to_showcase_dropdown_submit(self):
        '''
        Submitting 'Add to showcase' form with selected showcase value creates
        a sc/pkg association.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        showcase_one = factories.Dataset(name='my-first-showcase', type='showcase')
        factories.Dataset(name='my-second-showcase', type='showcase')
        factories.Dataset(name='my-third-showcase', type='showcase')

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}

        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='dataset_showcase_list', id=dataset['id']),
            extra_environ=env
        )

        form = response.forms['showcase-add']
        form['showcase_added'] = showcase_one['id']
        showcase_add_response = submit_and_follow(app, form, env)

        # returns to the correct page
        nosetools.assert_equal(showcase_add_response.request.path, "/dataset/showcases/my-dataset")
        # an association is created
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 1)

    def test_dataset_showcase_page_remove_showcase_button_submit(self):
        '''
        Submitting 'Remove' form with selected showcase value deletes a sc/pkg
        association.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        showcase_one = factories.Dataset(name='my-first-showcase', type='showcase')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_showcase_package_association_create',
                            context=context, package_id=dataset['id'],
                            showcase_id=showcase_one['id'])

        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 1)

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                        action='dataset_showcase_list', id=dataset['id']),
            extra_environ=env
        )

        # Submit the remove form.
        form = response.forms[1]
        nosetools.assert_equal(form['remove_showcase_id'].value, showcase_one['id'])
        showcase_remove_response = submit_and_follow(app, form, env)

        # returns to the correct page
        nosetools.assert_equal(showcase_remove_response.request.path, "/dataset/showcases/my-dataset")
        # the association is deleted
        nosetools.assert_equal(model.Session.query(ShowcasePackageAssociation).count(), 0)


class TestShowcaseAdminManageView(ShowcaseFunctionalTestBase):

    '''Plugin adds a showcase admin management page to ckan-admin section.'''

    def test_ckan_admin_has_showcase_config_tab(self):
        '''
        ckan-admin index page has a showcase config tab.
        '''
        if not tk.check_ckan_version(min_version='2.4'):
            raise SkipTest('Showcase config tab only available for CKAN 2.4+')

        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='admin', action='index'),
            extra_environ=env
        )
        # response contains link to dataset's showcase list
        nosetools.assert_true('/ckan-admin/showcase_admins' in response)

    def test_showcase_admin_manage_page_returns_correct_status(self):
        '''
        /ckan-admin/showcase_admins can be successfully accessed.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        app.get(url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                            action='manage_showcase_admins'),
                status=200, extra_environ=env)

    def test_showcase_admin_manage_page_lists_showcase_admins(self):
        '''
        Showcase admins are listed on the showcase admin page.
        '''
        app = self._get_test_app()
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_showcase_admin_add', context={},
                            username=user_two['name'])

        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                                       action='manage_showcase_admins'),
                           status=200, extra_environ=env)

        nosetools.assert_true('/user/{0}'.format(user_one['name']) in response)
        nosetools.assert_true('/user/{0}'.format(user_two['name']) in response)
        nosetools.assert_true('/user/{0}'.format(user_three['name']) not in response)

    def test_showcase_admin_manage_page_no_admins_message(self):
        '''
        Showcase admins page displays message if no showcase admins present.
        '''
        app = self._get_test_app()

        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(url=url_for(controller='ckanext.showcase.controller:ShowcaseController',
                                       action='manage_showcase_admins'),
                           status=200, extra_environ=env)

        nosetools.assert_true('There are currently no Showcase Admins' in response)


class TestSearch(helpers.FunctionalTestBase):

    def test_search_with_nonascii_filter_query(self):
        '''
        Searching with non-ASCII filter queries works.

        See https://github.com/ckan/ckanext-showcase/issues/34.
        '''
        app = self._get_test_app()
        tag = u'\xe4\xf6\xfc'
        dataset = factories.Dataset(tags=[{'name': tag, 'state': 'active'}])
        result = helpers.call_action('package_search', fq='tags:' + tag)
        nosetools.assert_equals(result['count'], 1)

