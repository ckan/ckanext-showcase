from ckanext.showcase.model import setup as showcase_setup


try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers


class ShowcaseFunctionalTestBase(helpers.FunctionalTestBase):

    def setup(self):
        '''Reset the database and clear the search indexes.'''
        super(ShowcaseFunctionalTestBase, self).setup()
        # set up showcase tables
        showcase_setup()
