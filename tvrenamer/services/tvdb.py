import logging

from tvdbapi_client import api
from tvdbapi_client import exceptions

from tvrenamer.services import base

LOG = logging.getLogger(__name__)


def _as_str(error):
    resp = getattr(error,  'response',  None)
    return str(error) if resp is None else resp.reason


class TvdbService(base.Service):
    """Provides access thetvdb data service to lookup TV Series information."""

    def __init__(self):
        super(TvdbService, self).__init__()
        self.api = api.TVDBClient()

    def get_series_by_name(self, series_name):
        """Perform lookup for series

        :param str series_name: series name found within filename
        :returns: instance of series
        :rtype: object
        """
        try:
            return self.api.search_series(name=series_name), None
        except exceptions.TVDBRequestException as err:
            LOG.exception('search for series %s failed', series_name)
            return None, _as_str(err)

    def get_series_by_id(self, series_id):
        """Perform lookup for series

        :param int series_id: series id of series
        :returns: instance of series
        :rtype: object
        """
        try:
            return self.api.get_series(series_id), None
        except exceptions.TVDBRequestException as err:
            LOG.exception('search for series %s failed', series_id)
            return None, _as_str(err)

    def get_series_name(self, series):
        """Perform lookup for name of series

        :param object series: instance of a series
        :returns: name of series
        :rtype: str
        """
        return series.get('seriesName')

    def _get_epname(self, episodes, epno, absolute=False):

        epname = None
        for ep in episodes:
            if int(ep.get('airedEpisodeNumber', -1)) == int(epno):
                epname = ep.get('episodeName')
                break
            if absolute and int(ep.get('absoluteNumber', -1)) == int(epno):
                epname = ep.get('episodeName')
                break

        return epname

    def get_episode_name(self, series, episode_numbers, season_number):
        """Perform lookup for name of episode numbers for a given series.

        :param object series: instance of a series
        :param list episode_numbers: the episode sequence number
        :param int season_number: numeric season of series
        :returns: list of episode name
        :rtype: list(str)
        """
        try:
            episodes = self.api.get_episodes(series.get('id'),
                                             airedSeason=season_number)
        except exceptions.TVDBRequestException as err:
            LOG.exception('episodes for series %s season no %s failed',
                          series.get('id'), season_number)
            return None, _as_str(err)

        epnames = []
        for epno in episode_numbers:
            epname = self._get_epname(episodes, epno)
            if epname is None:
                epname = self._get_epname(episodes, epno, absolute=True)
                if epname is None:
                    return None, None

            epnames.append(epname)

        return epnames, None
