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


def setup():
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


class ShowcasePackageAssociation(DomainObject):
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
    def create(cls, **kwargs):
        showcase_package_association = cls(**kwargs)
        Session.add(showcase_package_association)
        Session.commit()
        return showcase_package_association.as_dict()


def define_showcase_package_association_table():
        global showcase_package_assocation_table

        showcase_package_assocation_table = Table('showcase_package_association', metadata,
                                                  Column('package_id', types.UnicodeText,
                                                         ForeignKey('package.id'),
                                                         primary_key=True, nullable=False),
                                                  Column('showcase_id', types.UnicodeText,
                                                         ForeignKey('package.id'),
                                                         primary_key=True, nullable=False)
                                                  )

        mapper(ShowcasePackageAssociation, showcase_package_assocation_table)
