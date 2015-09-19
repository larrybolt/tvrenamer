"""Provides access to cache API for saving data."""
from oslo_config import cfg
import six

from tvrenamer.cache import api
from tvrenamer.cache import models

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


def save(instance):
    """Saves an instance of an episode in the cache.

    :param tvrenamer.core.episode.Episode instance: an instance of an episode
    :return: media file cache instance
    :rtype: :class:`~tvrenamer.cache.models.MediaFile`
    """
    mf = models.MediaFile()
    for name, value in six.iteritems(instance.__dict__):
        if name.startswith('_'):
            continue
        if hasattr(mf, name):
            if isinstance(value, list):
                value = ','.join(str(v) for v in value)
            setattr(mf, name, value)

    return dbapi().save(mf)
