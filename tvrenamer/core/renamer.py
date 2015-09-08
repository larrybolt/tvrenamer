import logging
import os
import shutil

from oslo_config import cfg

LOG = logging.getLogger(__name__)


def execute(filename, formatted_name):
    """Renames a file based on the name generated using metadata.

    :param str filename: absolute path and filename of original file
    :param str formatted_name: absolute path and new filename
    """

    if os.path.isfile(formatted_name):
        # If the destination exists, skip rename unless overwrite enabled
        if not cfg.CONF.overwrite_file_enabled:
            LOG.info('File %s already exists not forcefully moving %s',
                     formatted_name, filename)
            return

    LOG.info('renaming [%s] to [%s]', filename, formatted_name)
    if not cfg.CONF.dryrun:
        shutil.move(filename, formatted_name)
