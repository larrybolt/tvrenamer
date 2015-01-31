import logging

from oslo.config import cfg
import tvrage_api

from tvrenamer.services import base

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('language', 'tvrenamer.options')
cfg.CONF.import_opt('output_series_replacements', 'tvrenamer.options')


def as_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return -1


class TvrageService(base.Service):

    def get_series_by_name(self, series_name):
        """Perform lookup for series

        :param str series_name: series name found within filename
        :returns: instance of series
        :rtype: object
        """
        try:
            return tvrage_api.search_show(name=series_name), None
        except tvrage_api.TvrageException as err:
            LOG.exception('search by name failed')
            return None, err

    def get_series_by_id(self, series_id):
        """Perform lookup for series

        :param int series_id: series id of series
        :returns: instance of series
        :rtype: object
        """
        try:
            return tvrage_api.search_show(sid=series_id), None
        except tvrage_api.TvrageException as err:
            LOG.exception('search by id failed')
            return None, err

    def get_series_name(self, series):
        """Perform lookup for name of series

        :param object series: instance of a series
        :returns: name of series
        :rtype: str
        """
        if series is None:
            return None
        substitute_name = cfg.CONF.output_series_replacements
        if substitute_name:
            return substitute_name.get(series.name.lower(), series.name)
        return series.name

    def get_episode_name(self, series, episode_numbers, season_number=None):
        """Perform lookup for name of episode numbers for a given series.

        :param object series: instance of a series
        :param list episode_numbers: the episode sequence number
        :param int season_number: numeric season of series (default: None)
        :returns: name of episode
        :rtype: str
        """
        if series is None:
            LOG.warning('no series provided when requesting episode name')
            return None, None

        if season_number is None:
            LOG.debug('no season number, defaulting to 1')
            season_no = 1
        else:
            season_no = season_number

        epnames = []
        for epno in episode_numbers:
            try:
                episode = series.episode(as_int(season_no), as_int(epno))
                epnames.append(episode.name)
            except tvrage_api.TvrageException as err:
                LOG.exception('episode lookup failed')
                return None, err

        return epnames, None
