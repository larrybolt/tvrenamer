"""
Represents the state of a TV Episode based on a filename and additional
information from a data service.

Available actions on the Episode:

    - validate: verify file has potential to be a TV Episode
    - parse: retrieve information about TV Episode from elements of name
    - enhance: lookup additional information based on parsed elements
    - rename: change the name of file based on most up-to-date info
              and optionally change location.

The only input is an absolute path of a filename. Everything is controlled
via the provided configuration.
"""
import logging
import os

from oslo_config import cfg
import six

from tvrenamer import constants as const
from tvrenamer.core import formatter
from tvrenamer.core import parser
from tvrenamer.core import renamer
from tvrenamer import exceptions as exc
from tvrenamer import services

LOG = logging.getLogger(__name__)


def state(pre, post, attr='state'):
    """State decorator"""

    def decorator(method):
        @six.wraps(method)
        def inner(self, *args, **kwargs):
            setattr(self, attr, pre)
            result = method(self, *args, **kwargs)
            setattr(self, attr, post)
            return result
        return inner
    return decorator


class Episode(object):
    """Represents a TV episode."""

    def __init__(self, epfile):
        """:param str epfile: absolute path and filename of media file"""

        self.original = epfile
        self.name = os.path.basename(epfile)
        self.location = os.path.dirname(epfile)
        self.extension = os.path.splitext(epfile)[1]

        self.clean_name = None

        self.episode_numbers = None
        self.episode_names = None
        self.season_number = None
        self.series_name = None

        self.formatted_filename = None
        self.formatted_dirname = None
        self.out_location = None

        self._api = None
        self.messages = []
        self.state = const.INIT

    def __str__(self):
        return ('{0} => [{1} {2}|{3} {4}] '
                'meta: [{5} S{6} E{7}] '
                'formatted: {8}/{9}'.format(
                    self.original,
                    self.location,
                    self.name,
                    self.clean_name,
                    self.extension,
                    self.series_name or '',
                    self.season_number or '',
                    list(zip(
                        self.episode_numbers or [],
                        self.episode_names or [])),
                    self.formatted_dirname or '',
                    self.formatted_filename or ''))

    __repr__ = __str__

    def __call__(self):
        """Provides ability to perform processing consistently."""
        try:
            self.parse()
            self.enhance()
            self.format_name()
            self.rename()
            self.state = const.DONE
        except Exception as err:
            if not isinstance(err, exc.BaseTvRenamerException):
                LOG.exception('processing exception occurred')
                self.messages.append(str(err))
            self.state = const.FAILED

        return self

    @property
    def api(self):
        if self._api is None:
            self._api = services.get_service()
        return self._api

    @property
    def status(self):
        """Provides current status of processing episode.

        Structure of status:

            original_filename => formatted_filename, state, messages

        :returns: mapping of current processing state
        :rtype: dict
        """
        return {
            self.original: {
                'formatted_filename': self.out_location,
                'state': self.state,
                'messages': '\n\t'.join(self.messages),
                }
            }

    @state(pre=const.PREPARSE, post=const.POSTPARSE)
    def parse(self):
        """Extracts component keys from filename.

        :raises tvrenamer.exceptions.InvalidFilename:
            when filename was not parseable
        :raises tvrenamer.exceptions.ConfigValueError:
            when regex used for parsing was incorrectly configured
        """

        self.clean_name = formatter.apply_replacements(
            self.name, cfg.CONF.input_filename_replacements)

        output = parser.parse_filename(self.clean_name)

        if output is None:
            self.messages.append(
                'Invalid filename: unable to parse {0}'.format(
                    self.clean_name))
            LOG.info(self.messages[-1])
            raise exc.InvalidFilename(self.messages[-1])

        self.episode_numbers = output.get('episode_numbers')
        if self.episode_numbers is None:
            self.messages.append(
                'Regex does not contain episode number group, '
                'should contain episodenumber, episodenumber1-9, '
                'or episodenumberstart and episodenumberend\n\n'
                'Pattern was:\n' + output.get('pattern'))
            LOG.info(self.messages[-1])
            raise exc.ConfigValueError(self.messages[-1])

        self.series_name = output.get('series_name')
        if self.series_name is None:
            self.messages.append(
                'Regex must contain seriesname. Pattern was:\n' +
                output.get('pattern'))
            LOG.info(self.messages[-1])
            raise exc.ConfigValueError(self.messages[-1])

        self.series_name = formatter.clean_series_name(self.series_name)
        self.season_number = output.get('season_number')

    @state(pre=const.PREENHANCE, post=const.POSTENHANCE)
    def enhance(self):
        """Load metadata from a data service to improve naming.

        :raises tvrenamer.exceptions.ShowNotFound:
            when unable to find show/series name based on parsed name
        :raises tvrenamer.exceptions.EpisodeNotFound:
            when unable to find episode name(s) based on parsed data
        """

        series, error = self.api.get_series_by_name(self.series_name)

        if series is None:
            self.messages.append(str(error))
            LOG.info(self.messages[-1])
            raise exc.ShowNotFound(str(error))

        self.series_name = self.api.get_series_name(series)
        self.episode_names, error = self.api.get_episode_name(
            series, self.episode_numbers, self.season_number)

        if self.episode_names is None:
            self.messages.append(str(error))
            LOG.info(self.messages[-1])
            raise exc.EpisodeNotFound(str(error))

    @state(pre=const.PREFORMAT, post=const.POSTFORMAT)
    def format_name(self):
        """Formats the media file based on enhanced metadata.

        The actual name of the file and even the name of the directory
        structure where the file is to be stored.
        """
        self.formatted_filename = formatter.format_filename(
            self.series_name, self.season_number,
            self.episode_numbers, self.episode_names,
            self.extension)

        self.formatted_dirname = self.location
        if cfg.CONF.move_files_enabled:
            self.formatted_dirname = formatter.format_location(
                self.series_name, self.season_number)

        self.out_location = os.path.join(self.formatted_dirname,
                                         self.formatted_filename)

    @state(pre=const.PRENAME, post=const.POSTNAME)
    def rename(self):
        """Renames media file to formatted name.

        After parsing data from initial media filename and searching
        for additional data to using a data service, a formatted
        filename will be generated and the media file will be renamed
        to the generated name and optionally relocated.
        """
        renamer.execute(self.original, self.out_location)
        if cfg.CONF.move_files_enabled:
            LOG.debug('relocated: %s', self)
        else:
            LOG.debug('renamed: %s', self)
