from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import types

from ckan.model.domain_object import DomainObject
from ckan.model.meta import metadata, mapper, Session
from ckan import model

import logging
log = logging.getLogger(__name__)


showcase_package_assocation_table = None
showcase_admin_table = None


def setup():
    # setup showcase_package_assocation_table
    if showcase_package_assocation_table is None:
        define_showcase_package_association_table()
        log.debug('ShowcasePackageAssociation table defined in memory')

    if model.package_table.exists():
        if not showcase_package_assocation_table.exists():
            showcase_package_assocation_table.create()
            log.debug('ShowcasePackageAssociation table create')
        else:
            log.debug('ShowcasePackageAssociation table already exists')
    else:
        log.debug('ShowcasePackageAssociation table creation deferred')

    # setup showcase_admin_table
    if showcase_admin_table is None:
        define_showcase_admin_table()
        log.debug('ShowcaseAdmin table defined in memory')

    if model.user_table.exists():
        if not showcase_admin_table.exists():
            showcase_admin_table.create()
            log.debug('ShowcaseAdmin table create')
        else:
            log.debug('ShowcaseAdmin table already exists')
    else:
        log.debug('ShowcaseAdmin table creation deferred')


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


class ShowcasePackageAssociation(ShowcaseBaseModel):

    @classmethod
    def get_package_ids_for_showcase(cls, showcase_id):
        '''
        Return a list of package ids associated with the passed showcase_id.
        '''
        showcase_package_association_list = \
            Session.query(cls.package_id).filter_by(
                showcase_id=showcase_id).all()
        return showcase_package_association_list

    @classmethod
    def get_showcase_ids_for_package(cls, package_id):
        '''
        Return a list of showcase ids associated with the passed package_id.
        '''
        showcase_package_association_list = \
            Session.query(cls.showcase_id).filter_by(
                package_id=package_id).all()
        return showcase_package_association_list


def define_showcase_package_association_table():
    global showcase_package_assocation_table

    showcase_package_assocation_table = Table(
        'showcase_package_association', metadata,
        Column('package_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False),
        Column('showcase_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False)
    )

    mapper(ShowcasePackageAssociation, showcase_package_assocation_table)


class ShowcaseAdmin(ShowcaseBaseModel):

    @classmethod
    def get_showcase_admin_ids(cls):
        '''
        Return a list of showcase admin user ids.
        '''
        id_list = [i for (i, ) in Session.query(cls.user_id).all()]
        return id_list

    @classmethod
    def is_user_showcase_admin(cls, user):
        '''
        Determine whether passed user is in the showcase admin list.
        '''
        return (user.id in cls.get_showcase_admin_ids())


def define_showcase_admin_table():
    global showcase_admin_table

    showcase_admin_table = Table('showcase_admin', metadata,
                                 Column('user_id', types.UnicodeText,
                                        ForeignKey('user.id',
                                                   ondelete='CASCADE',
                                                   onupdate='CASCADE'),
                                        primary_key=True, nullable=False))

    mapper(ShowcaseAdmin, showcase_admin_table)
