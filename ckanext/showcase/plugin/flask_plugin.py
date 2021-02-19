# -*- coding: utf-8 -*-

import ckan.plugins as p
import ckanext.showcase.views as views

from ckanext.showcase.commands import cli


class MixinPlugin(p.SingletonPlugin):
    p.implements(p.IBlueprint)
    p.implements(p.IClick)

    # IBlueprint

    def get_blueprint(self):
        return views.get_blueprints()

    # IClick

    def get_commands(self):
        return cli.get_commands()
