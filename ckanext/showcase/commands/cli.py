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
def markdown_to_html():
    '''
        showcase markdown-to-html
    '''
    utils.markdown_to_html()


def get_commands():
    return [showcase]