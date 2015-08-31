import errno
import logging
import os
import shutil

from oslo_config import cfg

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('dryrun', 'tvrenamer.options')
cfg.CONF.import_opt('overwrite_file_enabled', 'tvrenamer.options')


def execute(filename, formatted_name):
    """Renames a file based on the name generated using metadata.

    :param str filename: absolute path and filename of original file
    :param str formatted_name: absolute path and new filename
    :raises: OSError if unable rename file
    """

    if os.path.isfile(formatted_name):
        # If the destination exists, raise exception unless force is True
        if not cfg.CONF.overwrite_file_enabled:
            LOG.warning('File %s already exists not forcefully moving %s',
                        formatted_name, filename)
            raise OSError(errno.EEXIST,
                          'File already exists, not overwriting.', filename)

    LOG.info('renaming [%s] to [%s]', filename, formatted_name)
    if not cfg.CONF.dryrun:
        shutil.move(filename, formatted_name)
