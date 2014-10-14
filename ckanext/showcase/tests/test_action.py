from nose.tools import assert_equals
import mock

import ckan.new_tests.helpers as helpers
import ckan.new_tests.factories as factories

# import ckanext.showcase.logic.action as action


class TestShowcaseAction(object):

    @mock.patch('ckan.new_authz.auth_is_loggedin_user')
    def test_showing_group_in_showing_list_for_user(self, mockauth):
        '''
        The showings_list_admin action returns a showing group created by the
        user.
        '''
        mockauth.return_value = True

        showing_admin = factories.User()

        showing_group = factories.Group(type='showing', user=showing_admin)

        showing_list = helpers.call_action('showings_list_admin', context={'user': showing_admin.get('name')})
        assert_equals(len(showing_list), 1)
        assert_equals(showing_list[0]['name'], showing_group['name'])
        assert_equals(showing_list[0]['type'], 'showing')

    @mock.patch('ckan.new_authz.auth_is_loggedin_user')
    def test_showing_group_in_showing_list_for_user_excludes_normal_groups(self, mockauth):
        '''
        The showings_list_admin action returns a showing group created by the
        user, but doesn't contains normal groups created by user.
        '''
        mockauth.return_value = True

        showing_admin = factories.User()

        factories.Group(user=showing_admin)
        showing_group = factories.Group(type='showing', user=showing_admin)

        showing_list = helpers.call_action('showings_list_admin', context={'user': showing_admin.get('name')})
        assert_equals(len(showing_list), 1)
        assert_equals(showing_list[0]['name'], showing_group['name'])
        assert_equals(showing_list[0]['type'], 'showing')
