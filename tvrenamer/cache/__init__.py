"""Provides access to cache API for saving data."""
from oslo_config import cfg

from tvrenamer.cache import api

_DBAPI = None


def dbapi(conf=cfg.CONF):
    """Retrieves an instance of the configured database API.

    :param oslo_config.cfg.ConfigOpts conf: an instance of the configuration
                                            file
    :return: database API instance
    :rtype: :class:`~tvrenamer.cache.api.DatabaseAPI`
    """
    global _DBAPI

    if _DBAPI is None:
        _DBAPI = api.DatabaseAPI(conf)
    return _DBAPI
