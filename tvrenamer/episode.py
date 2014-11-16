"""
Represents the state of a TV Episode based on a filename and additional
information from a data service.

Available actions on the Episode:

    - validate: verify file has potential to be a TV Episode
    - parse: retrieve information about TV Episode from elements of name
    - enhance: lookup additional information based on parsed elements
    - rename: change the name of file based on most up-to-date info
    - relocate: change location and name of file based on most up-to-date info

Helper actions:

    - generate_filename: formats a new filename based on info available.
    - generate_dirname: formats a directory path based on info available.
    - execute_rename: handles logic on whether to relocate or rename.

The only input is an absolute path of a filename. Everything is controlled
via the provided configuration.
"""
import logging
import os

from oslo.config import cfg

from tvrenamer.common import tools
from tvrenamer import exceptions as exc
from tvrenamer import formatter
from tvrenamer import parser
from tvrenamer import renamer
from tvrenamer.services import tvdb

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('filename_blacklist', 'tvrenamer.options')
cfg.CONF.import_opt('input_filename_replacements', 'tvrenamer.options')
cfg.CONF.import_opt('library_base_path', 'tvrenamer.options')
cfg.CONF.import_opt('move_files_enabled', 'tvrenamer.options')
cfg.CONF.import_opt('valid_extensions', 'tvrenamer.options')


class Episode(object):

    def __init__(self, epfile):

        self.original = epfile
        self.name = os.path.basename(epfile)
        self.location = os.path.dirname(epfile)
        self.extension = os.path.splitext(epfile)[1]

        self._valid = None
        self.clean_name = None

        self.episode_numbers = None
        self.season_number = None
        self.series_name = None
        self.extra_values = None
        self.episode_names = None

        self.formatted_filename = None
        self.formatted_dirname = None

        self.api = tvdb.TvdbService()
        self.messages = []

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
                                             zip(self.episode_numbers or [],
                                                 self.episode_names or []),
                                             self.formatted_dirname or '',
                                             self.formatted_filename or ''))

    __repr__ = __str__

    @property
    def valid(self):
        if self._valid is not None:
            return self._valid
        return self.validate()

    @valid.setter
    def valid(self, val):
        self._valid = val

    def validate(self):

        self.messages = []
        self.valid = True

        if not os.access(self.original, os.R_OK):
            self.valid = False
            self.messages.append(
                'File {0} is not accessible/readable.'.format(
                    self.original))
            LOG.info(self.messages[-1])

        if not tools.is_valid_extension(self.extension,
                                        cfg.CONF.valid_extensions):
            self.valid = False
            self.messages.append(
                'Extension {0} is blacklisted.'.format(self.extension))
            LOG.info(self.messages[-1])

        if tools.is_blacklisted_filename(self.original,
                                         self.name,
                                         cfg.CONF.filename_blacklist):
            self.valid = False
            self.messages.append(
                'File {0} is blacklisted.'.format(self.name))
            LOG.info(self.messages[-1])

        _, self.extension = tools.split_extension(self.name)
        self.clean_name = tools.apply_replacements(
            self.name, cfg.CONF.input_filename_replacements)

        return self.valid

    def parse(self):

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

        self.extra_values = output.get('extra_values')
        self.season_number = output.get('season_number')

    def enhance(self):
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

    def generate_filename(self):

        self.formatted_filename = formatter.format_filename(
            self.series_name, self.season_number,
            self.episode_numbers, self.episode_names,
            self.extra_values, self.extension)
        return self.formatted_filename

    def generate_dirname(self):
        self.formatted_dirname = formatter.format_dirname(
            self.series_name, self.season_number,
            self.episode_numbers, self.name)
        return self.formatted_dirname

    def rename(self):
        renamer.execute_rename(self.original,
                               os.path.join(self.location,
                                            self.generate_filename()))

    def relocate(self):
        renamer.execute_relocate(self.original,
                                 os.path.join(cfg.CONF.library_base_path,
                                              self.generate_dirname(),
                                              self.generate_filename()))

    def execute_rename(self):
        if cfg.CONF.move_files_enabled:
            self.relocate()
            LOG.debug('relocated: %s', self)
        else:
            self.rename()
            LOG.debug('renamed: %s', self)
