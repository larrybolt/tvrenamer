import errno
import logging
import os
import shutil

from oslo.config import cfg

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('dryrun', 'tvrenamer.options')
cfg.CONF.import_opt('overwrite_file_enabled', 'tvrenamer.options')


def _rename_file(old, new):
    LOG.info('rename %s to %s', old, new)
    stat = os.stat(old)
    os.rename(old, new)
    try:
        os.utime(new, (stat.st_atime, stat.st_mtime))
    except OSError as ex:
        if ex.errno == errno.EPERM:
            LOG.warning('File times not preserved for %s', new)
        else:
            raise


def _check_overwrite_existing(filename, formatted_name):
    if os.path.isfile(formatted_name):
        # If the destination exists, raise exception unless force is True
        if not cfg.CONF.overwrite_file_enabled:
            LOG.warning('File %s already exists not forcefully moving %s',
                        formatted_name, filename)
            raise OSError()


def execute_rename(filename, formatted_name):

    _check_overwrite_existing(filename, formatted_name)
    LOG.info('inplace-rename [%s] to [%s]', filename, formatted_name)
    if not cfg.CONF.dryrun:
        # just rename the file to move it
        _rename_file(filename, formatted_name)


def execute_relocate(filename, formatted_name):

    _check_overwrite_existing(filename, formatted_name)

    formatted_dirname = os.path.dirname(formatted_name)
    if not os.path.isdir(formatted_dirname):
        try:
            if not cfg.CONF.dryrun:
                os.makedirs(formatted_dirname)
                LOG.info('Created directory %s', formatted_dirname)
        except OSError as e:
            LOG.exception('making library path failed (%s)',
                          formatted_dirname)
            if e.errno != errno.EEXIST:
                raise

    if os.stat(filename).st_dev == os.stat(formatted_dirname).st_dev:
        # Same partition, just rename the file to move it
        LOG.info('move-rename [%s] to [%s]', filename, formatted_name)
        if not cfg.CONF.dryrun:
            _rename_file(filename, formatted_name)
    else:
        LOG.info('copy-rename [%s] to [%s]', filename, formatted_name)
        # File is on different partition (different disc), copy it
        if not cfg.CONF.dryrun:
            shutil.copy2(filename, formatted_name)
            # Forced to move file, we just trash old file
            LOG.info('Deleting %s', filename)
            os.unlink(filename)
