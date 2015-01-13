import logging
import logging.handlers

from testtools import matchers

from tvrenamer import service
from tvrenamer.tests import base


class ServiceTest(base.BaseTest):

    cfg_data = []
    cfg_data.append('[loggers]\n')
    cfg_data.append('keys = root\n')
    cfg_data.append('\n')
    cfg_data.append('[logger_root]\n')
    cfg_data.append('level = DEBUG\n')
    cfg_data.append('handlers = consoleHandler\n')
    cfg_data.append('\n')
    cfg_data.append('[formatters]\n')
    cfg_data.append('keys = simple\n')
    cfg_data.append('\n')
    cfg_data.append('[formatter_simple]\n')
    cfg_data.append(
        'format = %(asctime)s - %(name)s - %(levelname)s - %(message)s\n')
    cfg_data.append('\n')
    cfg_data.append('[handlers]\n')
    cfg_data.append('keys = consoleHandler\n')
    cfg_data.append('\n')
    cfg_data.append('[handler_consoleHandler]\n')
    cfg_data.append('class=StreamHandler\n')
    cfg_data.append('level=DEBUG\n')
    cfg_data.append('formatter=simple\n')
    cfg_data.append('args=(sys.stdout,)\n')

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
                                          ''.join(self.cfg_data))],
                                        '.log')[0]
        self.CONF.set_override('logconfig', logfile)
        service._setup_logging()
        root = logging.getLogger()
        self.assertEqual(logging.DEBUG, root.getEffectiveLevel())

    def test_configure(self):
        pass

    def test_prepare_service(self):
        pass
