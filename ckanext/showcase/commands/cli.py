# -*- coding: utf-8 -*-

import click

from ckanext.showcase import utils

# Click commands for CKAN 2.9 and above


@click.group()
def showcase():
    '''showcase commands
    '''
    pass


@showcase.command()
@click.option('--allow-duplicates',
                default=False,
                help='Allow related items with duplicate titles to be migrated. Duplicate showcases will be created as "duplicate_<related-name>_<related-id>".')
def migrate(allow_duplicates):
    """
        showcase migrate [options]
    """
    utils.migrate(allow_duplicates)


@showcase.command()
def markdown_to_html():
    '''
        showcase markdown-to-html
    '''
    utils.markdown_to_html()


def get_commands():
    return [showcase]