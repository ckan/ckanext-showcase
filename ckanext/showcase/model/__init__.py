from sqlalchemy import Column, ForeignKey, types

from ckan.model.domain_object import DomainObject
from ckan.model.meta import Session
from ckanext.showcase.data.constants import *

import logging

try:
    from ckan.plugins.toolkit import BaseModel
except ImportError:
    # CKAN <= 2.9
    from ckan.model.meta import metadata
    from sqlalchemy.ext.declarative import declarative_base

    BaseModel = declarative_base(metadata=metadata)

log = logging.getLogger(__name__)


class ShowcaseBaseModel(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        instance = cls.filter(**kwargs).first()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance.as_dict()


class ShowcasePackageAssociation(ShowcaseBaseModel, BaseModel):

    __tablename__ = "showcase_package_association"

    package_id = Column(
        types.UnicodeText,
        ForeignKey("package.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    showcase_id = Column(
        types.UnicodeText,
        ForeignKey("package.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    @classmethod
    def get_package_ids_for_showcase(cls, showcase_id):
        """
        Return a list of package ids associated with the passed showcase_id.
        """
        showcase_package_association_list = (
            Session.query(cls.package_id).filter_by(showcase_id=showcase_id).all()
        )
        return showcase_package_association_list

    @classmethod
    def get_showcase_ids_for_package(cls, package_id):
        """
        Return a list of showcase ids associated with the passed package_id.
        """
        showcase_package_association_list = (
            Session.query(cls.showcase_id) \
            .filter_by(package_id=package_id) \
            .join(ShowcaseApprovalStatus, cls.showcase_id == ShowcaseApprovalStatus.showcase_id)
            .filter(ShowcaseApprovalStatus.status == ApprovalStatus.PENDING)
            .all()
        )
        return showcase_package_association_list


class ShowcaseAdmin(ShowcaseBaseModel, BaseModel):
    __tablename__ = "showcase_admin"

    user_id = Column(
        types.UnicodeText,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    @classmethod
    def get_showcase_admin_ids(cls):
        """
        Return a list of showcase admin user ids.
        """
        id_list = [i for (i,) in Session.query(cls.user_id).all()]
        return id_list

    @classmethod
    def is_user_showcase_admin(cls, user):
        """
        Determine whether passed user is in the showcase admin list.
        """
        return user.id in cls.get_showcase_admin_ids()

class ShowcaseApprovalStatus(ShowcaseBaseModel, BaseModel):
    __tablename__ = "showcase_approval"

    # TODO Check if date fields are required
    
    showcase_id = Column(
        types.UnicodeText,
        ForeignKey("package.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    feedback = Column(types.UnicodeText, nullable=True)
    status = Column(
        types.Enum(
            ApprovalStatus, 
            name="status_enum"
            ), 
        nullable=False, 
        default=ApprovalStatus.PENDING
    )


    @classmethod
    def get_status_for_showcase(cls, showcase_id):
        """
        Return the feedback associated with the given showcase_id.
        """
        return cls.filter(showcase_id=showcase_id).all()

    @classmethod
    def update_status(cls, showcase_id, feedback, status=ApprovalStatus.PENDING):
        """
        Update feedback for the given feedback_id.
        """
        feedback_instance = cls.get(showcase_id=showcase_id)
        if feedback_instance:
            feedback_instance.feedback = feedback
            feedback_instance.status = status
            Session.commit()
            return feedback_instance.as_dict()
        else:
            return cls.create(
                showcase_id=showcase_id,
                feedback = feedback,
                status = status
            )