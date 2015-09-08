import logging
import logging.config
import logging.handlers
import os
import sys

from oslo_config import cfg
import six
from six import moves

import tvrenamer
from tvrenamer import options
from tvrenamer import services

logging.getLogger().addHandler(logging.NullHandler())

DEFAULT_LIBRARY_LOG_LEVEL = {'stevedore': logging.WARNING,
                             'requests': logging.WARNING,
                             'tvdbapi_client': logging.WARNING,
                             }
CONSOLE_MESSAGE_FORMAT = '%(message)s'
LOG_FILE_MESSAGE_FORMAT = '[%(asctime)s] %(levelname)-8s %(name)s %(message)s'


def _setup_logging():

    root_logger = logging.getLogger()
    root_logger.setLevel(cfg.CONF.loglevel.upper())

    # Set up logging to a file
    if cfg.CONF.logfile:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=cfg.CONF.logfile, maxBytes=1000 * 1024, backupCount=9)
        formatter = logging.Formatter(LOG_FILE_MESSAGE_FORMAT)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    if not cfg.CONF.cron:
        # Always send higher-level messages to the console via stderr
        console = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(CONSOLE_MESSAGE_FORMAT)
        console.setFormatter(formatter)
        root_logger.addHandler(console)

    # shut off logging from 3rd party frameworks
    for xlib, xlevel in six.iteritems(DEFAULT_LIBRARY_LOG_LEVEL):
        xlogger = logging.getLogger(xlib)
        xlogger.setLevel(xlevel)


def _configure(args):

    config_files = []
    virtual_path = os.getenv('VIRTUAL_ENV')
    cfg_file = '{0}.conf'.format(tvrenamer.PROJECT_NAME)

    # if virtualenv is active; then leverage <virtualenv>/etc
    # and <virtualenv>/etc/<project>
    if virtual_path:
        config_files.append(os.path.join(virtual_path, 'etc', cfg_file))
        config_files.append(os.path.join(virtual_path, 'etc',
                                         tvrenamer.PROJECT_NAME, cfg_file))

    config_files.extend(
        cfg.find_config_files(project=tvrenamer.PROJECT_NAME))

    cfg.CONF(args,
             project=tvrenamer.PROJECT_NAME,
             version=tvrenamer.__version__,
             default_config_files=list(moves.filter(os.path.isfile,
                                                    config_files)))

    # if no config_dir was provided then we will set it to the
    # path of the most specific config file found.
    if not cfg.CONF.config_dir and cfg.CONF.config_file:
        cfg.CONF.set_default('config_dir',
                             os.path.dirname(cfg.CONF.config_file[-1]))


def prepare_service(args=None):
    """Configures application and setups logging."""
    options.register_opts(cfg.CONF)
    services.load_service_opts(cfg.CONF)
    _configure(args)
    _setup_logging()

    cfg.CONF.log_opt_values(logging.getLogger(), logging.DEBUG)
