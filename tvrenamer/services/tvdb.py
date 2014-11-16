import logging

from oslo.config import cfg
import tvdb_api

from tvrenamer.services import base

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('language', 'tvrenamer.options')
cfg.CONF.import_opt('output_series_replacements', 'tvrenamer.options')


class TvdbService(base.Service):

    def __init__(self):
        super(TvdbService, self).__init__()
        self.api = tvdb_api.Tvdb(language=cfg.CONF.language)

    def get_series_by_name(self, series_name):
        """Perform lookup for series

        :param str series_name: series name found within filename
        :returns: instance of series
        :rtype: object
        """
        return self._get_series(series_name)

    def get_series_by_id(self, series_id):
        """Perform lookup for series

        :param int series_id: series id of series
        :returns: instance of series
        :rtype: object
        """
        return self._get_series(series_id)

    def _get_series(self, key):
        try:
            return self.api[key], None
        except tvdb_api.tvdb_error as err:
            LOG.error('Error with thetvdb: %s', err)
            return None, err
        except tvdb_api.tvdb_shownotfound as nferr:
            LOG.error('Show %s not found on thetvdb: %s', key, nferr)
            return None, nferr
        except tvdb_api.tvdb_userabort as uaerr:
            LOG.error('user abort: %s', uaerr)
            return None, uaerr

    def get_series_name(self, series):
        """Perform lookup for name of series

        :param object series: instance of a series
        :returns: name of series
        :rtype: str
        """
        if series is None:
            return None
        series_name = series['seriesname']
        substitute_name = cfg.CONF.output_series_replacements
        if substitute_name:
            return substitute_name.get(series_name.lower(), series_name)
        return series_name

    def get_episode_name(self, series, episode_numbers, season_number=None):
        """Perform lookup for name of episode numbers for a given series.

        :param object series: instance of a series
        :param list episode_numbers: the episode sequence number
        :param int season_number: numeric season of series (default: None)
        :returns: name of episode
        :rtype: list(str)
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
                episodeinfo = series[season_no][epno]
            except tvdb_api.tvdb_seasonnotfound as snferr:
                LOG.error('Season could not be found: %s', snferr)
                return None, snferr
            except tvdb_api.tvdb_episodenotfound as enferr:
                # Try to search by absolute_number
                sr = series.search(epno, 'absolute_number')
                if len(sr) > 1:
                    # For multiple results try and make sure there is a
                    # direct match
                    unsure = True
                    for e in sr:
                        if int(e['absolute_number']) == epno:
                            epnames.append(e['episodename'])
                            unsure = False
                    # If unsure error out
                    if unsure:
                        LOG.error('No episode actually matches %s, found %s '
                                  'results instead', epno, len(sr))
                        return None, None
                elif len(sr) == 1:
                    epnames.append(sr[0]['episodename'])
                else:
                    LOG.error('Episode of show could not be found (also '
                              'tried searching by absolute episode number): '
                              '%s', enferr)
                    return None, enferr

            except tvdb_api.tvdb_attributenotfound:
                LOG.error('Could not find episode name for %s', epno)
                return None, None
            else:
                epnames.append(episodeinfo['episodename'])

        return epnames, None
