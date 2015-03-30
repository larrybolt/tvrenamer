"""Provides access to cache API for saving data."""
from oslo_config import cfg

from tvrenamer.cache import api
from tvrenamer.cache import models

OPTS = [
    cfg.BoolOpt('enabled',
                default=True,
                help='Enable caching results'),
    cfg.StrOpt('connection',
               default='sqlite:///$config_dir/cache.db',
               help='The connection string used to connect to the database'),
    cfg.IntOpt('idle_timeout',
               default=3600,
               help='Timeout before idle sql connections are reaped'),
    cfg.IntOpt('connection_debug',
               default=0,
               help='Verbosity of SQL debugging information. 0=None, 100=All'),
]

cfg.CONF.register_opts(OPTS, 'database')

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


def list_opts():
    """Returns a list of oslo_config options available in the library.

    The returned list includes all oslo_config options which may be registered
    at runtime by the library.

    Each element of the list is a tuple. The first element is the name of the
    group under which the list of elements in the second element will be
    registered. A group name of None corresponds to the [DEFAULT] group in
    config files.

    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users by this library.

    :returns: a list of (group_name, opts) tuples
    """
    from tvrenamer.common import tools
    return tools.make_opt_list([OPTS], 'database')
