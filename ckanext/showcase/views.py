# -*- coding: utf-8 -*-

from flask import Blueprint


import ckan.lib.helpers as h
import ckan.plugins.toolkit as tk
import ckan.views.dataset as dataset

import ckanext.showcase.utils as utils

showcase = Blueprint(u'showcase_blueprint', __name__)


def index():
    return dataset.search(utils.DATASET_TYPE_NAME)


class CreateView(dataset.CreateView):
    def get(self, data=None, errors=None, error_summary=None):
        utils.check_new_view_auth()
        return super(CreateView, self).get(utils.DATASET_TYPE_NAME, data,
                                           errors, error_summary)

    def post(self):

        data_dict = dataset.clean_dict(
            dataset.dict_fns.unflatten(
                dataset.tuplize_dict(dataset.parse_params(tk.request.form))))
        data_dict.update(
            dataset.clean_dict(
                dataset.dict_fns.unflatten(
                    dataset.tuplize_dict(dataset.parse_params(
                        tk.request.files)))))
        context = self._prepare()
        data_dict['type'] = utils.DATASET_TYPE_NAME

        try:
            pkg_dict = tk.get_action('ckanext_showcase_create')(context,
                                                                data_dict)

        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            data_dict['state'] = 'none'
            return self.get(data_dict, errors, error_summary)

        # redirect to manage datasets
        url = h.url_for('showcase_blueprint.manage_datasets',
                        id=pkg_dict['name'])
        return h.redirect_to(url)


def manage_datasets(id):
    return utils.manage_datasets_view(id)


def delete(id):
    return utils.delete_view(id)


def read(id):
    return utils.read_view(id)


class EditView(dataset.EditView):
    def get(self, id, data=None, errors=None, error_summary=None):
        utils.check_new_view_auth()
        return super(EditView, self).get(utils.DATASET_TYPE_NAME, id, data,
                                         errors, error_summary)

    def post(self, id):
        context = self._prepare()
        utils.check_edit_view_auth(id)

        data_dict = dataset.clean_dict(
            dataset.dict_fns.unflatten(
                dataset.tuplize_dict(dataset.parse_params(tk.request.form))))
        data_dict.update(
            dataset.clean_dict(
                dataset.dict_fns.unflatten(
                    dataset.tuplize_dict(dataset.parse_params(
                        tk.request.files)))))

        data_dict['id'] = id
        try:
            pkg = tk.get_action('ckanext_showcase_update')(context, data_dict)
        except tk.ValidationError as e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.get(id, data_dict, errors, error_summary)

        tk.c.pkg_dict = pkg

        # redirect to showcase details page
        url = h.url_for('showcase_blueprint.read', id=pkg['name'])
        return h.redirect_to(url)


def dataset_showcase_list(id):
    return utils.dataset_showcase_list(id)


def admins():
    return utils.manage_showcase_admins()


def admin_remove():
    return utils.remove_showcase_admin()


def upload():
    return utils.upload()


showcase.add_url_rule('/showcase', view_func=index)
showcase.add_url_rule('/showcase/new', view_func=CreateView.as_view('new'))
showcase.add_url_rule('/showcase/delete/<id>',
                      view_func=delete,
                      methods=[u'GET', u'POST'])
showcase.add_url_rule('/showcase/<id>', view_func=read)
showcase.add_url_rule('/showcase/edit/<id>',
                      view_func=EditView.as_view('edit'),
                      methods=[u'GET', u'POST'])
showcase.add_url_rule('/showcase/manage_datasets/<id>',
                      view_func=manage_datasets,
                      methods=[u'GET', u'POST'])
showcase.add_url_rule('/dataset/showcases/<id>',
                      view_func=dataset_showcase_list,
                      methods=[u'GET', u'POST'])
showcase.add_url_rule('/ckan-admin/showcase_admins',
                      view_func=admins,
                      methods=[u'GET', u'POST'])
showcase.add_url_rule('/ckan-admin/showcase_admin_remove',
                      view_func=admin_remove,
                      methods=[u'GET', u'POST'])
showcase.add_url_rule('/showcase_upload',
                      view_func=upload,
                      methods=[u'POST'])


def get_blueprints():
    return [showcase]
