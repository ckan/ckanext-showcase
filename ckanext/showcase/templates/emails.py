from ckan.common import _, config
import ckan.lib.helpers as h


class EmailTemplates():
    @classmethod
    def site_title(cls):
        return config.get('ckan.site_title')
    

    @classmethod
    def site_url(cls):
        return config.get('ckan.site_url')


    @classmethod
    def footer_lines(cls):
        return [
            _("Have a nice day."),
            "---",
            _(f"Message sent by { cls.site_title() } ({ cls.site_url() })")
        ]

    @classmethod
    def compose_email_body(cls, lines, body_vars):
        user_name = body_vars['user_name']

        text = "\n\n".join(
            [_(f"Dear {user_name},")] + lines + cls.footer_lines()
            )
        return text

    
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']
        opening_word = body_vars['opening_word']
        action_url = h.url_for('showcase_blueprint.read', id = showcase['id']),


        lines = [
            _(f"{opening_word} resuse case was submitted to Portal Supervisor for review."),
            _(f"You can check the current status of your resuse case at {cls.site_url() + action_url[0]}"),
        ]

        return cls.compose_email_body(lines, body_vars)


    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']
        action_url = h.url_for('showcase_blueprint.read', id = showcase['id']),

        lines = [
            _(f"Status of reuse case \'{showcase['display_title']}\' was updated to {showcase['status']}."),
            _(f"You can check the current status of resuse at {cls.site_url() + action_url[0]}"),
        ]

        return cls.compose_email_body(lines, body_vars)


class SubjectTemplates():
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']

        return  _(f"Reuse case \'{showcase['display_title']}\' was submitted for review.")


    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']

        return _(f"Reuse case \'{showcase['display_title']}\' status was updated."),



class NotificationTemplates():
    @classmethod
    def compose_email_body(cls, lines, body_vars):
        text = "\n\n".join(lines)
        return text

    
    @classmethod
    def get_showcase_create(cls, body_vars):
        showcase = body_vars['showcase']
        opening_word = body_vars['opening_word']


        lines = [
            _(f"{opening_word} resuse case was submitted to the Portal Supervisor for review."),
        ]

        return cls.compose_email_body(lines, body_vars)

    @classmethod
    def get_status_update(cls, body_vars):
        showcase = body_vars['showcase']

        lines = [
            _(f"Status of reuse case \'{showcase['display_title']}\' was updated to {showcase['status']}."),
        ]

        return cls.compose_email_body(lines, body_vars)

