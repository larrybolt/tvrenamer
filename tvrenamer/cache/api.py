"""Private database API implemented for database operations."""
import logging

import tinydb

LOG = logging.getLogger(__name__)


class DatabaseAPI(object):
    """Public APIs to perform on the database."""

    def __init__(self, conf):
        """Initialize new instance.

        :param conf: an instance of configuration file
        :type conf: oslo_config.cfg.ConfigOpts
        """
        self.conf = conf
        self.dbi = tinydb.TinyDB(conf.cache.dbfile)

    def clear(self):
        """Clear database."""
        self.dbi.purge_tables()

    def update(self, instance, condition):
        """Update the instance to the database

        :param instance: an instance of modeled data object
        :param condition: condition evaluated to determine record(s) to update
        :returns: record id updated or None
        :rtype: int
        """
        item = self.dbi.get(condition)
        if item is None:
            return None
        item.update(instance.as_dict())
        self.dbi.update(item, condition)
        return item.eid

    def create(self, instance):
        """Create the instance to the database

        :param instance: an instance of modeled data object
        :returns: record id of created record
        :rtype: int
        """
        return self.dbi.insert(instance.as_dict())

    def save(self, instance):
        """Save (create or update) the instance to the database

        :param instance: an instance of modeled data object
        """
        cond = tinydb.where('original') == instance.original
        eid = self.update(instance, cond)
        if eid is None:
            return self.create(instance)
        return eid
