from sqlalchemy import Column, ForeignKey, types, or_, func
import datetime
from ckan.model.domain_object import DomainObject
from ckan.model.meta import Session
from ckanext.showcase.data.constants import *
from ckan.model.meta import Session
from ckan import model
from ckanext.showcase import utils

import logging

from six import text_type
from sqlalchemy.orm import class_mapper
try:
    from sqlalchemy.engine import Row
except ImportError:
    try:
        from sqlalchemy.engine.result import RowProxy as Row
    except ImportError:
        from sqlalchemy.engine.base import RowProxy as Row


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
    status_modified = Column(types.DateTime, default=datetime.datetime.utcnow)


    @classmethod
    def get_status_for_showcase(cls, showcase_id):
        return cls.filter(showcase_id=showcase_id).first()

    @classmethod
    def update_status(cls, showcase_id, feedback='', status=ApprovalStatus.PENDING):
        feedback_instance = cls.get(showcase_id=showcase_id)
        if feedback_instance:
            feedback_instance.feedback = feedback
            feedback_instance.status = status
            feedback_instance.status_modified = datetime.datetime.now()
            Session.commit()
            return feedback_instance.as_dict()
        else:
            return cls.create(
                showcase_id=showcase_id,
                feedback = feedback,
                status = status
            )
        

    def as_dict(self):
        result_dict = {}

        if isinstance(self, Row):
            fields = self.keys()
        else:
            ModelClass = self.__class__
            table = class_mapper(ModelClass).mapped_table
            fields = [field.name for field in table.c]

        for name in fields:
            value = getattr(self, name)

            if value is None\
            or isinstance(value, dict)\
            or isinstance(value, int)\
            or isinstance(value, list):
                result_dict[name] = value
            elif isinstance(value, Enum):
                result_dict[name] = value.value
                if name == 'status':
                    result_dict['display_status'] = SHOWCASE_STATUS_OPTIONS[value.value]

            elif isinstance(value, datetime.datetime):
                result_dict[name] = value.isoformat()
            else:
                result_dict[name] = text_type(value)

        return result_dict


    @classmethod
    def generate_statistics(cls, creator_user_id=None):
        session = Session()
        
        # Base query
        query = session.query(cls)\
            .join(model.Package, model.Package.id == cls.showcase_id)\
            .filter(model.Package.type == utils.DATASET_TYPE_NAME)\
            .filter(model.Package.state == 'active')

        if creator_user_id:
            query = query.filter(model.Package.creator_user_id == creator_user_id)

        total_count = query.count()
        
        # Breakdown by status
        status_breakdown = query.with_entities(
            cls.status, func.count(cls.showcase_id)
        ).group_by(cls.status).all()
        
        status_dict = {status.value: count for status, count in status_breakdown}
        
        statistics = {
            'total': total_count,
            'status_breakdown': status_dict,
        }
        
        return statistics
    
    @classmethod
    def filter_showcases(cls, **kwargs):
        query = Session.query(model.Package.id) \
                .filter(model.Package.type == utils.DATASET_TYPE_NAME) \
                .filter(model.Package.state == 'active') \
                .join(cls, model.Package.id == ShowcaseApprovalStatus.showcase_id)
                # TODO do we need an outer join

        query = cls.filter_by_search_query(query, kwargs.pop('q', ''))
        
        query = cls.filter_by_date(
            query,
            created_start=kwargs.pop('created_start', None),
            created_end=kwargs.pop('created_end', None),
        )
        
        sort_fields = kwargs.pop('sort', 'metadata_created desc').split()
        sort_field, sort_order = sort_fields[0], sort_fields[1]

        query = cls.filter_by_status(
            query, 
            status = kwargs.pop('status', '')        
        )
        
        query = cls.filter_by_creator_user_id(
            query,
            creator_user_id=kwargs.pop('creator_user_id', '')
        )
        
        
        if sort_field:
            if hasattr(model.Package, sort_field):
                required_class = model.Package
            elif hasattr(cls, sort_field):
                required_class = cls
            if required_class:
                if sort_order == 'desc':
                    query = query.order_by(getattr(required_class, sort_field).desc())
                else:
                    query = query.order_by(getattr(required_class, sort_field).asc())
        
        return query

    @classmethod
    def filter_by_search_query(cls, query, search_query):
        search_terms = search_query.split()
        
        if search_terms:
            title_conditions = [model.Package.title.ilike(f'%{word}%') for word in search_terms]
            notes_conditions = [model.Package.notes.ilike(f'%{word}%') for word in search_terms]
            name_conditions = [model.Package.name.ilike(f'%{word}%') for word in search_terms]

            combined_conditions = or_(*title_conditions, *notes_conditions, *name_conditions)
            query = query.filter(combined_conditions)
        
        return query
    

    @classmethod
    def filter_by_status(cls, query, status = None):
        if not status:  return query

        status = cls.convert_status_to_enum(status)
        query = query.filter(ShowcaseApprovalStatus.status==status)
        return query


    @classmethod
    def convert_status_to_enum(cls, status=None):
        if not status:  return ApprovalStatus.PENDING
        showcase_status_map = {status_item.value: status_item.name for status_item in ApprovalStatus}
        return ApprovalStatus[showcase_status_map[status]]
    

    @classmethod
    def filter_by_date(cls, query, created_start=None, created_end=None):
        if created_start:
            created_start = created_start.date()
            query = query.filter(func.date(model.Package.metadata_created) >= created_start)

        if created_end:
            created_end = created_end.date()
            query = query.filter(func.date(model.Package.metadata_created) <= created_end)

        return query
    
    @classmethod
    def filter_by_creator_user_id(cls, query, creator_user_id=None):
        if creator_user_id:
            query = query \
                    .filter(model.Package.creator_user_id == creator_user_id)
        
        return query
