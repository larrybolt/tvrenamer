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
    cfg_data.append('#logconfig =\n')
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

    log_cfg_data = []
    log_cfg_data.append('[loggers]\n')
    log_cfg_data.append('keys = root\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[logger_root]\n')
    log_cfg_data.append('level = DEBUG\n')
    log_cfg_data.append('handlers = consoleHandler\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[formatters]\n')
    log_cfg_data.append('keys = simple\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[formatter_simple]\n')
    log_cfg_data.append(
        'format = %(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[handlers]\n')
    log_cfg_data.append('keys = consoleHandler\n')
    log_cfg_data.append('\n')
    log_cfg_data.append('[handler_consoleHandler]\n')
    log_cfg_data.append('class=StreamHandler\n')
    log_cfg_data.append('level=DEBUG\n')
    log_cfg_data.append('formatter=simple\n')
    log_cfg_data.append('args=(sys.stdout,)\n')

    def test_setup_logging(self):
        del logging.getLogger().handlers[:]
        service._setup_logging()
        self.assertEqual(logging.getLogger().getEffectiveLevel(),
                         logging.INFO)
        self.assertEqual(logging.getLogger('tvdb_api').getEffectiveLevel(),
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

    def test_setup_logging_via_file(self):
        logfile = self.create_tempfiles([('tvrenamer',
                                          ''.join(self.log_cfg_data))],
                                        '.log')[0]
        self.CONF.set_override('logconfig', logfile)
        service._setup_logging()
        root = logging.getLogger()
        self.assertEqual(logging.DEBUG, root.getEffectiveLevel())

    def test_configure_with_venv(self):

        cfg.CONF.reset()
        cfg.CONF.import_opt('libraries', 'tvrenamer.options')

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

        cfg.CONF.reset()
        cfg.CONF.import_opt('libraries', 'tvrenamer.options')

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
        cfg.CONF.import_opt('libraries', 'tvrenamer.options')

        with fixtures.EnvironmentVariable('VIRTUAL_ENV'):
            cfgfile = self.create_tempfiles(
                [(os.path.join(os.path.expanduser('~'),
                               'tvrenamer'),
                    ''.join(self.cfg_data))])[0]
            self.addCleanup(os.removedirs, os.path.dirname(cfgfile))
            self.addCleanup(os.unlink, cfgfile)
            service.prepare_service([])

        self.assertEqual(logging.getLogger('tvdb_api').getEffectiveLevel(),
                         logging.WARNING)
        self.assertEqual(cfg.CONF.libraries, ['/tmp/junk'])
