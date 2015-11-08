import logging
import os

from oslo_config import cfg
import trakt
from trakt.core import exceptions

from tvrenamer.services import base

LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt(
        'client_id',
        secret=True,
        default=os.environ.get('TRAKT_CLIENT_ID'),
        help='client id from your trakt account ENV[\'TRAKT_CLIENT_ID\']'),
    cfg.StrOpt(
        'client_secret',
        secret=True,
        default=os.environ.get('TRAKT_CLIENT_SECRET'),
        help='client secret from your trakt account '
             'ENV[\'TRAKT_CLIENT_SECRET\']'),
]

cfg.CONF.register_opts(OPTS, 'trakt')


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
    return tools.make_opt_list([OPTS], 'trakt')


class TraktService(base.Service):
    """Provides access trakt data service to lookup TV Series information.

    `Trakt.tv <http://trakt.tv/>`_

    Services used from trakt:

    - search series by name
    - lookup series by id
    - get episode name(s) by season number and episode number(s)
    """

    def __init__(self):
        super(TraktService, self).__init__()
        trakt.Trakt.configuration.defaults.client(
            id=cfg.CONF.trakt.client_id,
            secret=cfg.CONF.trakt.client_secret)

    def get_series_by_name(self, series_name):
        """Perform lookup for series

        :param str series_name: series name found within filename
        :returns: instance of series
        :rtype: object
        """
        series = trakt.Trakt['search'].query(series_name, 'show')
        if not series:
            return None, 'Not Found'
        return series[0], None

    def get_series_by_id(self, series_id):
        """Perform lookup for series

        :param int series_id: series id of series
        :returns: instance of series
        :rtype: object
        """
        series = trakt.Trakt['search'].lookup(series_id, 'trakt-show')
        if not series:
            return None, 'Not Found'
        return series, None

    def get_series_name(self, series):
        """Perform lookup for name of series

        :param object series: instance of a series
        :returns: name of series
        :rtype: str
        """
        return series.title

    def get_episode_name(self, series, episode_numbers, season_number):
        """Perform lookup for name of episode numbers for a given series.

        :param object series: instance of a series
        :param list episode_numbers: the episode sequence number
        :param int season_number: numeric season of series
        :returns: list of episode name
        :rtype: list(str)
        """
        ids = series.to_identifier()
        series_id = ids['ids']['trakt']

        epnames = []
        for epno in episode_numbers:
            try:
                episode = trakt.Trakt['shows'].episode(
                    series_id, season_number, epno, exceptions=True)
            except exceptions.RequestError as err:
                LOG.exception('fetch episode %s S%sE%s failed',
                              series_id, season_number, epno)
                return None, str(err)

            epnames.append(episode.title)

        return epnames, None
