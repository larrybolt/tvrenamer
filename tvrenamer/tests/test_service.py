import logging
import logging.handlers
import os
import tempfile

import fixtures
from oslo_config import cfg
from testtools import matchers

from tvrenamer import service
from tvrenamer.tests import base


class ServiceTest(base.BaseTest):

    cfg_data = []
    cfg_data.append('[DEFAULT]\n')
    cfg_data.append('#cron = false\n')
    cfg_data.append('#default_library =\n')
    cfg_data.append('#directory_name_format = .\n')
    cfg_data.append('#dryrun = false\n')
    cfg_data.append('#episode_separator = -\n')
    cfg_data.append('#episode_single = %02d\n')
    cfg_data.append('#filename_blacklist =\n')
    cfg_data.append('#filename_character_blacklist =\n')
    cfg_data.append(
        '#filename_format_ep = %(seriesname)s - %(seasonnumber)02dx%(episode)s - %(episodename)s%(ext)s\n')  # noqa
    cfg_data.append('#input_filename_replacements =\n')
    cfg_data.append('#input_series_replacements =\n')
    cfg_data.append('#language = en\n')
    cfg_data.append('libraries = /tmp/junk\n')
    cfg_data.append('#locations =\n')
    cfg_data.append('#logfile = tvrenamer.log\n')
    cfg_data.append('#loglevel = info\n')
    cfg_data.append('#move_files_enabled = false\n')
    cfg_data.append(
        '#multiep_format = %(epname)s (%(episodemin)s-%(episodemax)s)\n')
    cfg_data.append('#multiep_join_name_with = ", "\n')
    cfg_data.append('#output_filename_replacements =\n')
    cfg_data.append('#output_series_replacements =\n')
    cfg_data.append('#overwrite_file_enabled = false\n')
    cfg_data.append('#replacement_character = _\n')
    cfg_data.append('#valid_extensions =\n')
    cfg_data.append('\n')

    def test_setup_logging(self):
        del logging.getLogger().handlers[:]
        service._setup_logging()
        self.assertEqual(logging.getLogger().getEffectiveLevel(),
                         logging.INFO)
        self.assertEqual(
            logging.getLogger('tvdbapi_client').getEffectiveLevel(),
            logging.WARNING)

        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.handlers.RotatingFileHandler),
                    matchers.IsInstance(logging.StreamHandler),
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_no_logfile(self):
        self.CONF.set_override('logfile', None)
        del logging.getLogger().handlers[:]
        service._setup_logging()
        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.StreamHandler),
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_cron(self):
        self.CONF.set_override('cron', True)
        del logging.getLogger().handlers[:]
        service._setup_logging()
        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.handlers.RotatingFileHandler),
                    matchers.IsInstance(logging.NullHandler)))

    def test_setup_logging_no_logging(self):
        self.CONF.set_override('logfile', None)
        self.CONF.set_override('cron', True)
        del logging.getLogger().handlers[:]
        service._setup_logging()
        for hndler in logging.getLogger().handlers:
            self.assertThat(
                hndler,
                matchers.MatchesAny(
                    matchers.IsInstance(logging.NullHandler)))

    def test_configure_with_venv(self):

        vdir = tempfile.mkdtemp()
        dirname = os.path.join(vdir, 'etc')
        os.mkdir(dirname)
        self.addCleanup(os.removedirs, dirname)

        with fixtures.EnvironmentVariable('VIRTUAL_ENV', vdir):
            cfgfile = self.create_tempfiles(
                [(os.path.join(dirname, 'tvrenamer'),
                  ''.join(self.cfg_data))])[0]
            self.addCleanup(os.unlink, cfgfile)
            service._configure([])
            self.assertEqual(cfg.CONF.libraries, ['/tmp/junk'])

    def test_configure_without_venv(self):

        with fixtures.EnvironmentVariable('VIRTUAL_ENV'):
            cfgfile = self.create_tempfiles(
                [(os.path.join(os.path.expanduser('~'),
                               'tvrenamer'),
                    ''.join(self.cfg_data))])[0]
            self.addCleanup(os.removedirs, os.path.dirname(cfgfile))
            self.addCleanup(os.unlink, cfgfile)
            service._configure([])
            self.assertEqual(cfg.CONF.libraries, ['/tmp/junk'])

    def test_prepare_service(self):

        cfg.CONF.reset()

        with fixtures.EnvironmentVariable('VIRTUAL_ENV'):
            cfgfile = self.create_tempfiles(
                [(os.path.join(os.path.expanduser('~'),
                               'tvrenamer'),
                    ''.join(self.cfg_data))])[0]
            self.addCleanup(os.removedirs, os.path.dirname(cfgfile))
            self.addCleanup(os.unlink, cfgfile)
            service.prepare_service([])

        self.assertEqual(
            logging.getLogger('tvdbapi_client').getEffectiveLevel(),
            logging.WARNING)
        self.assertEqual(cfg.CONF.libraries, ['/tmp/junk'])
