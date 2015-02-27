from routes import url_for
from nose import tools as nosetools

import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

import logging
log = logging.getLogger(__name__)

submit_and_follow = helpers.submit_and_follow


class TestShowcaseIndex(helpers.FunctionalTestBase):

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


class TestShowcaseNewView(helpers.FunctionalTestBase):

    def test_showcase_create_form_renders(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController', action='new'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_showcase_new_redirects_to_add_datasets(self):
        '''Creating a new showcase redirects to the add datasets form.'''
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

        # Unique to add_datasets page
        nosetools.assert_true('bulk_action.showcase_add' in create_response)
        # Requested page is the add_datasets url.
        nosetools.assert_equal(url_for(controller='ckanext.showcase.controller:ShowcaseController',
                                       action='add_datasets', id='my-showcase'), create_response.request.path)


class TestShowcaseEditView(helpers.FunctionalTestBase):

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

    def test_showcase_edit_redirects_to_add_datasets(self):
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


class TestDatasetView(helpers.FunctionalTestBase):

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
