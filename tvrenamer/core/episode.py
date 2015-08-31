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

from tvrenamer.common import tools
from tvrenamer import constants as const
from tvrenamer.core import formatter
from tvrenamer.core import parser
from tvrenamer.core import renamer
from tvrenamer import exceptions as exc
from tvrenamer import services

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('filename_blacklist', 'tvrenamer.options')
cfg.CONF.import_opt('input_filename_replacements', 'tvrenamer.options')
cfg.CONF.import_opt('output_series_replacements', 'tvrenamer.options')
cfg.CONF.import_opt('default_library', 'tvrenamer.options')
cfg.CONF.import_opt('libraries', 'tvrenamer.options')
cfg.CONF.import_opt('move_files_enabled', 'tvrenamer.options')
cfg.CONF.import_opt('valid_extensions', 'tvrenamer.options')


class Episode(object):
    """Represents a TV episode."""

    def __init__(self, epfile):
        """:param str epfile: absolute path and filename of media file"""

        self.original = epfile
        self.name = os.path.basename(epfile)
        self.location = os.path.dirname(epfile)
        self.extension = os.path.splitext(epfile)[1]

        self._valid = None
        self.clean_name = None

        self.episode_numbers = None
        self.episode_names = None
        self.season_number = None
        self.series_name = None

        self.formatted_filename = None
        self.formatted_dirname = None

        self.api = services.get_service()
        self.messages = []
        self.state = const.INIT

    def __str__(self):
        return ('<{0}>:{1} => [{2} {3}|{4} {5}] '
                'meta: [{6} S{7} E{8}] '
                'formatted: {9}/{10}'.format(self.__class__.__name__,
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
            self.rename()
            self.state = const.DONE
        except Exception as err:
            if not isinstance(err, exc.BaseTvRenamerException):
                LOG.exception('processing exception occurred')
                self.messages.append(str(err))
            self.state = const.FAILED

        return self

    @property
    def valid(self):
        """Provides flag to indicate a valid file.

        :returns: True if all validations passed else False
        :rtype: bool
        """
        if self._valid is not None:
            return self._valid
        return self.validate()

    @property
    def status(self):
        """Provides current status of processing episode.

        Structure of status:

            original_filename => formatted_filename, state, result, messages

        :returns: mapping of current processing state
        :rtype: dict
        """
        return {
            self.original: {
                'formatted_filename': self.formatted_filename,
                'progress': self.state,
                'result': len(self.messages) == 0,
                'messages': '\n\t'.join(self.messages),
                }
            }

    @tools.state(pre=const.PREVALID, post=const.POSTVALID)
    def validate(self):
        """Performs all validation checks to allow processing to continue.

        :returns: True if all validations passed else False
        :rtype: bool
        """

        if not os.access(self.original, os.R_OK):
            self._valid = False
            self.messages.append(
                'File {0} is not accessible/readable.'.format(
                    self.original))
            LOG.info(self.messages[-1])
            return self.valid

        if not tools.is_valid_extension(self.extension,
                                        cfg.CONF.valid_extensions):
            self._valid = False
            self.messages.append(
                'Extension {0} is blacklisted.'.format(self.extension))
            LOG.info(self.messages[-1])
            return self.valid

        if tools.is_blacklisted_filename(self.original,
                                         self.name,
                                         cfg.CONF.filename_blacklist):
            self._valid = False
            self.messages.append(
                'File {0} is blacklisted.'.format(self.name))
            LOG.info(self.messages[-1])
            return self.valid

        self.clean_name = tools.apply_replacements(
            self.name, cfg.CONF.input_filename_replacements)

        # if made it to this point then must be valid
        self._valid = True

        return self.valid

    @tools.state(pre=const.PREPARSE, post=const.POSTPARSE)
    def parse(self):
        """Extracts component keys from filename.

        :raises tvrenamer.exceptions.NoValidFilesFoundError:
            when episode did not pass validations
        :raises tvrenamer.exceptions.InvalidFilename:
            when filename was not parseable
        :raises tvrenamer.exceptions.ConfigValueError:
            when regex used for parsing was incorrectly configured
        """

        if not self.valid:
            raise exc.NoValidFilesFoundError(';'.join(self.messages))

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
        else:
            self.series_name = formatter.clean_series_name(self.series_name)

        self.season_number = output.get('season_number')

    @tools.state(pre=const.PREENHANCE, post=const.POSTENHANCE)
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

        self.series_name = self.api.get_series_name(
            series, cfg.CONF.output_series_replacements)
        self.episode_names, error = self.api.get_episode_name(
            series, self.episode_numbers, self.season_number)

        if self.episode_names is None:
            self.messages.append(str(error))
            LOG.info(self.messages[-1])
            raise exc.EpisodeNotFound(str(error))

    @tools.state(pre=const.PREFORMAT, post=const.POSTFORMAT)
    def _format_filename(self):

        self.formatted_filename = formatter.format_filename(
            self.series_name, self.season_number,
            self.episode_numbers, self.episode_names,
            self.extension)

        return self.formatted_filename

    def _format_dirname(self):
        self.formatted_dirname = formatter.format_dirname(
            self.series_name, self.season_number)
        return self.formatted_dirname

    @tools.state(pre=const.PRENAME, post=const.POSTNAME)
    def rename(self):
        """Renames media file to formatted name.

        After parsing data from initial media filename and searching
        for additional data to using a data service, a formatted
        filename will be generated and the media file will be renamed
        to the generated name and optionally relocated.
        """

        if cfg.CONF.move_files_enabled:
            library_base_path = tools.find_library(self._format_dirname(),
                                                   cfg.CONF.libraries,
                                                   cfg.CONF.default_library)
            renamer.execute(self.original,
                            os.path.join(library_base_path,
                                         self.formatted_dirname,
                                         self._format_filename()))
            LOG.debug('relocated: %s', self)
        else:
            renamer.execute(self.original,
                            os.path.join(self.location,
                                         self._format_filename()))
            LOG.debug('renamed: %s', self)
