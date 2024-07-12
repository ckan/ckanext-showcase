from sqlalchemy import Column, ForeignKey, types

from ckan.model.domain_object import DomainObject
from ckan.model.meta import Session

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
            Session.query(cls.showcase_id).filter_by(package_id=package_id).all()
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
