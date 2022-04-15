# -*- coding: utf-8 -*-

from __future__ import print_function

from ckan.lib.cli import CkanCommand

from ckanext.showcase import utils

# Paster commands for CKAN 2.8 and below


class MigrationCommand(CkanCommand):
    '''
    ckanext-showcase migration command.

    Usage::

        paster showcase markdown-to-html -c <path to config file>
            - Migrate the notes of all showcases from markdown to html.

    Must be run from the ckanext-showcase directory.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(CkanCommand, self).__init__(name)

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print(self.__doc__)
            return

        cmd = self.args[0]
        self._load_config()

        if cmd == 'markdown-to-html':
            self.markdown_to_html()
        else:
            print('Command "{0}" not recognized'.format(cmd))

    def markdown_to_html(self):
        utils.markdown_to_html()
