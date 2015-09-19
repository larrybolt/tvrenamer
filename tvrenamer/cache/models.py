"""Provides database model compliant with sqlalchemy."""
import datetime
import re

import six
import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy import orm


def to_table_name(klass_name):
    """Generate table name based on class name.

    Convention is to take camel-case class name and rewrite it to an
    underscore form, e.g. 'ClassName' to 'class_name'

    :param klass_name: name of class
    :return: properly formatted table name
    :rtype: string
    """
    return re.sub('[A-Z]+',
                  lambda i: '_' + i.group(0).lower(),
                  klass_name).lstrip('_') + 's'


@declarative.as_declarative()
class Base(six.Iterator):
    """Represents a Base class mapped to table in the database."""

    @declarative.declared_attr
    def __tablename__(cls):
        return to_table_name(cls.__name__)

    def save(self, session):
        """Save this object.

        :param session: a database connection session
        """
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return '<%s.%s[object at %x] {%s}>' % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        """Retrieve value for an attribute in the table.

        :param key: name of field/attribute
        :param default: default value if not found
        :return: attribute value :rtype: varied
        """
        return getattr(self, key, default)

    def __iter__(self):
        self._i = iter(list(dict(orm.object_mapper(self).columns).keys()))
        return self

    def __next__(self):
        n = six.advance_iterator(self._i)
        return n, getattr(self, n)

    def next(self):
        """Using an iterator to get next attribute value from generator

        :return: attribute, attribute value
        :rtype: tuple
        """
        return self.__next__()

    def update(self, values):
        """Make the model object behave like a dict.

        :param values: key-value pairs of attributes and values
        """
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def iteritems(self):
        """an iterator over dictionary items

        :return: dictionary items
        :rtype: iterator
        """
        local = dict(self)
        joined = dict([(k, v) for k, v in six.iteritems(self.__dict__)
                      if not k[0] == '_'])
        local.update(joined)
        return six.iteritems(local)


class HasId(object):
    """Table mixin providing a class/table id attribute"""
    id = sa.Column(sa.Integer, primary_key=True)


class HasTimestamp(object):
    """Table mixin providing a class/table date attributes"""
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, onupdate=datetime.datetime.utcnow)


class MediaFile(Base, HasId, HasTimestamp):
    """Class representing a series media file processed."""

    __table_args__ = {
        'sqlite_autoincrement':  True,
    }
    original = sa.Column(sa.String(255))
    name = sa.Column(sa.String(100), default=None)
    extension = sa.Column(sa.String(20), default=None)
    location = sa.Column(sa.String(100), default=None)
    clean_name = sa.Column(sa.String(100), default=None)
    series_name = sa.Column(sa.String(100), default=None)
    season_number = sa.Column(sa.Integer, default=1)
    episode_numbers = sa.Column(sa.String(100), default=None)
    episode_names = sa.Column(sa.String(5000), default=None)
    formatted_filename = sa.Column(sa.String(255), default=None)
    formatted_dirname = sa.Column(sa.String(255), default=None)
    state = sa.Column(sa.String(20), default=None)
    messages = sa.Column(sa.String(5000), default=None)


def verify_tables(engine):
    """Creates all the defined tables within the database

    :param engine: database engine instance
    """
    Base.metadata.create_all(engine, checkfirst=True)


def purge_all_tables(engine):
    """Drops all the defined tables within the database

    :param engine: database engine instance
    """
    Base.metadata.drop_all(engine, checkfirst=True)
