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
        factories.Dataset(name='my-showcase')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.showcase.controller:ShowcaseController', action='new'),
            extra_environ=env,
        )

        # create showcase
        form = response.forms['dataset-edit']
        form['name'] = u'my-dataset'
        create_response = submit_and_follow(app, form, env, 'save')

        # Unique to add_datasets page
        nosetools.assert_true('bulk_action.showcase_add' in create_response)
