from ckan.lib.mailer import mail_user
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h
from ckan.common import config
from ckan import model
from ckan.lib.jobs import enqueue as enqueue_job
from ckanext.showcase.templates.emails import EmailTemplates, NotificationTemplates, SubjectTemplates

_ = tk._

import logging
log = logging.getLogger(__name__)

site_title = config.get('ckan.site_title')
site_url = config.get('ckan.site_url')


def _get_notification_context():
    return {
        'model': model,
        'user': tk.g.user or tk.g.author,
        'session': model.Session,
        'auth_user_obj': tk.g.userobj,
        'ignore_auth': True
    }

def _get_all_portal_admins():
    context = {
        'model': model,
        'session': model.Session,
        'user': tk.g.user or tk.g.author,
        'auth_user_obj': tk.g.userobj,
        'ignore_auth': True
    }
    members = tk.get_action('member_list')(context, {'id':'portal_administrator', 'type': 'user'})
    members = [member[0] for member in members]

    return members



def showcase_create(showcase_id):
    showcase = tk.get_action('ckanext_showcase_show')(_get_notification_context(), {'id': showcase_id})

    body_vars = {'showcase': showcase}
    action_url = site_url + h.url_for('showcase_blueprint.read', id = showcase['id'])

    # Requester
    requster = model.User.get(showcase.get('creator_user_id'))
    body_vars['user_name'] = requster.fullname or requster.name
    body_vars['opening_word'] = 'Your'


    _notify_user(requster, body_vars, 'get_showcase_create', action_url)


    body_vars['opening_word'] = 'A'

    # admins
    portal_admins = _get_all_portal_admins()
    body_vars['role'] = 'admin'

    for admin in portal_admins:
        user = model.User.get(admin)
        body_vars['user_name'] = user.fullname or user.name
        _notify_user(user, body_vars, 'get_showcase_create', action_url)


def status_update(showcase_id):
    showcase = tk.get_action('ckanext_showcase_show')(_get_notification_context(), {'id': showcase_id})
    showcase_status = tk.get_action('ckanext_showcase_status_show')(_get_notification_context(), {'showcase_id': showcase_id})
    
    showcase = {**showcase, **showcase_status}
    body_vars = {'showcase': showcase}
    action_url = site_url + h.url_for('showcase_blueprint.read', id = showcase['id'])

    # Requester
    requster = model.User.get(showcase.get('creator_user_id'))
    body_vars['user_name'] = requster.fullname or requster.name
    body_vars['opening_word'] = 'Your'

    _notify_user(user, body_vars, 'get_status_update', action_url)


    # admins
    portal_admins = _get_all_portal_admins()
    body_vars['role'] = 'admin'

    for admin in portal_admins:
        user = model.User.get(admin)
        body_vars['user_name'] = user.fullname or user.name
        _notify_user(user, body_vars, 'get_status_update', action_url)



def _notify_user(user, body_vars, template_name, action_url):

    subject_method = getattr(SubjectTemplates, template_name, None)
    
    # Check if method exists
    if subject_method:
        subject =  subject_method(body_vars)
    else:
        raise ValueError(f"Template method '{template_name}' not found.")

    notification_method = getattr(NotificationTemplates, template_name, None)

    # Check if method exists
    if notification_method:
        notification =  notification_method(body_vars)
    else:
        raise ValueError(f"Template method '{template_name}' not found.")


    body_method = getattr(EmailTemplates, template_name, None)

    # Check if method exists
    if body_method:
        body =  body_method(body_vars)
    else:
        raise ValueError(f"Template method '{template_name}' not found.")


    tk.get_action('generate_notification')(_get_notification_context(), {
            'user_id': user.id,
            'subject': subject,
            'body': notification,
            'action_url': action_url,
        })    
    
    queue_email_job(user, subject, body)    


def _send_email(user, subject, body):
    if user.email:
        try:
            log.info(f'ISSUE_EMAIL_LOG1 {user.email}')
            mail_user(user, subject, body)
            log.info(f'ISSUE_EMAIL_LOG2 {user.email}')
        except: 
            log.critical('Email sending failed.')


def queue_email_job(user, subject, body):
    """Queue the email job to be processed in the background."""
    enqueue_job(_send_email, args=[user, subject, body], title='Send Email',rq_kwargs={'timeout': 300})