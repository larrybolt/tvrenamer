"""Provides access to cache API for saving data."""
from oslo_config import cfg

from tvrenamer.cache import api
from tvrenamer.cache import models

MediaFile = models.MediaFile
_DBAPI = None


def dbapi(conf=cfg.CONF):
    """Retrieves an instance of the configured database API.

    :param oslo_config.cfg.ConfigOpts conf: an instance of the configuration
                                            file
    :return: database API instance
    :rtype: :class:`~tvrenamer.cache.api.Connection`
    """
    global _DBAPI

    if _DBAPI is None:
        _DBAPI = api.Connection(conf)
        _DBAPI.shrink_db()
    return _DBAPI
