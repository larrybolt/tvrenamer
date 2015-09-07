"""Private database API implemented for sqlalchemy for database operations."""
import logging

from tvrenamer.cache import models as db_model
from tvrenamer.cache import session as db_session

LOG = logging.getLogger(__name__)


class Connection(object):
    """SQLAlchemy connection."""

    def __init__(self, conf):
        """Initialize new instance.

        :param conf: an instance of configuration file
        :type conf: oslo_config.cfg.ConfigOpts
        """
        self.conf = conf
        self._engine_facade = db_session.EngineFacade.from_config(
            conf.cache.connection, conf)
        self.upgrade()

    def upgrade(self):
        """Migrate the database to `version` or most recent version."""
        engine = self._engine_facade.engine
        db_model.verify_tables(engine)
        engine.dispose()

    def clear(self):
        """Clear database."""
        engine = self._engine_facade.engine
        db_model.purge_all_tables(engine)
        self._engine_facade.session_maker.close_all()
        engine.dispose()

    def shrink_db(self):
        """Shrink database."""
        engine = self._engine_facade.engine
        with engine.begin() as conn:
            conn.execute('VACUUM')
            LOG.debug('db space reclaimed')

    def save(self, instance):
        """Save the instance to the database

        :param instance: an instance of modeled data object
        """
        instance.save(self._engine_facade.session)
        return instance
