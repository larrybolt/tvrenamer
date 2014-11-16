"""Command-line interface to the TvRenamer APIs"""

import logging
import os
import sys

from oslo.config import cfg
import six
from six import moves

import tvrenamer
from tvrenamer import api


if hasattr(logging, 'NullHandler'):
    NullHandler = logging.NullHandler
else:
    class NullHandler(logging.Handler):
        def handle(self, record):
            pass

        def emit(self, record):
            pass

        def createLock(self):
            self.lock = None

logging.getLogger().addHandler(NullHandler())

LOG = logging.getLogger(tvrenamer.PROJECT_NAME)

DEFAULT_LIBRARY_LOG_LEVEL = {'stevedore': logging.WARNING,
                             'requests': logging.WARNING,
                             'tvdb_api': logging.WARNING
                             }
CONSOLE_MESSAGE_FORMAT = '%(message)s'
LOG_FILE_MESSAGE_FORMAT = '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'

cfg.CONF.import_opt('locations', 'tvrenamer.options')
cfg.CONF.import_opt('dryrun', 'tvrenamer.options')
cfg.CONF.import_opt('logfile', 'tvrenamer.options')
cfg.CONF.import_opt('loglevel', 'tvrenamer.options')
cfg.CONF.import_opt('logconfig', 'tvrenamer.options')


def configure_logging():

    root_logger = logging.getLogger('')
    root_logger.setLevel(cfg.CONF.loglevel.upper())

    # Set up logging to a file
    if cfg.CONF.logfile:
        file_handler = logging.FileHandler(
            filename=cfg.CONF.logfile,
        )
        formatter = logging.Formatter(LOG_FILE_MESSAGE_FORMAT)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Always send higher-level messages to the console via stderr
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(cfg.CONF.loglevel.upper())
    formatter = logging.Formatter(CONSOLE_MESSAGE_FORMAT)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # shut off logging from 3rd party frameworks
    for xlib, xlevel in six.iteritems(DEFAULT_LIBRARY_LOG_LEVEL):
        xlogger = logging.getLogger(xlib)
        xlogger.setLevel(xlevel)


def configure(args):

    config_files = []
    virtual_path = os.getenv('VIRTUAL_ENV')
    CFG_FILE = '{0}.conf'.format(tvrenamer.PROJECT_NAME)
    # if virtualenv is active; then leverage <virtualenv>/etc
    # and <virtualenv>/etc/<project>
    if virtual_path:
        config_files.append(os.path.join(virtual_path, 'etc', CFG_FILE))
        config_files.append(os.path.join(virtual_path, 'etc',
                                         tvrenamer.PROJECT_NAME, CFG_FILE))

    config_files.extend(
        cfg.find_config_files(project=tvrenamer.PROJECT_NAME))

    cfg.CONF(args,
             project=tvrenamer.PROJECT_NAME,
             version=tvrenamer.__version__,
             default_config_files=list(moves.filter(os.path.isfile,
                                                    config_files)))


def main(args=sys.argv[1:]):
    configure(args)
    configure_logging()
    cfg.CONF.log_opt_values(LOG, logging.DEBUG)

    results = api.API.execute(cfg.CONF.locations)
    for epname, result in six.iteritems(results):
        status = 'SUCCESS' if result.get('result') else 'FAILURE'
        LOG.info('[%s]: %s --> %s', status, epname,
                 result.get('formatted_filename'))
        if result.get('messages'):
            LOG.error('\tREASON: %s', result.get('messages'))

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
