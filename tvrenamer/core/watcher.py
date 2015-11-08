import logging
import os
import re

from oslo_config import cfg

LOG = logging.getLogger(__name__)


def _is_valid_extension(extension):
    """Checks if the file extension is blacklisted in valid_extensions.

    :param str extension: a file extension to check
    :returns: flag indicating if the extension is valid based on list of
              valid extensions.
    :rtype: bool
    """
    if not cfg.CONF.valid_extensions:
        return True

    valid = False
    for cext in cfg.CONF.valid_extensions:
        if not cext.startswith('.'):
            cext = '.%s' % cext
        if extension == cext:
            valid = True
            break

    return valid


def _is_blacklisted_filename(filepath):
    """Checks if the filename matches filename_blacklist

    blacklist is a list of filenames(str) and/or file patterns(dict)

    string, specifying an exact filename to ignore
    [".DS_Store", "Thumbs.db"]

    mapping(dict), where each dict contains:
        'match' - (if the filename matches the pattern, the filename
        is blacklisted)

        'is_regex' - if True, the pattern is treated as a
        regex. If False, simple substring check is used (if
        'match' in filename). Default is False

        'full_path' - if True, full path is checked. If False, only
        filename is checked. Default is False.

        'exclude_extension' - if True, the extension is removed
        from the file before checking. Default is False.

    :param str filepath: an absolute path and filename to check against
                         the blacklist
    :returns: flag indicating if the file was matched in the blacklist
    :rtype: bool
    """

    if not cfg.CONF.filename_blacklist:
        return False

    filename = os.path.basename(filepath)
    fname = os.path.splitext(filename)[0]

    blacklisted = False
    for fblacklist in cfg.CONF.filename_blacklist:

        if isinstance(fblacklist, dict):
            to_check = filename
            if fblacklist.get('exclude_extension', False):
                to_check = fname
            if fblacklist.get('full_path', False):
                to_check = filepath

            if fblacklist.get('is_regex', False):
                blacklisted = re.match(fblacklist['match'],
                                       to_check) is not None
            else:
                blacklisted = (fblacklist['match'] in to_check)
        else:
            blacklisted = (filename == fblacklist)

        if blacklisted:
            break

    return blacklisted


def retrieve_files():
    """Get list of files found in provided locations.

    Search through the paths provided to find files for processing.

    :returns: absolute path of filename
    :rtype: list
    """

    all_files = []
    for location in cfg.CONF.locations or []:
        # if local path then make sure it is absolute
        if not location.startswith('\\'):
            location = os.path.abspath(os.path.expanduser(location))

        LOG.debug('searching [%s]', location)
        for root, _, files in os.walk(location):
            LOG.debug('found file(s) %s', files)
            for name in files:
                filepath = os.path.join(root, name)
                if (os.access(filepath, os.R_OK) and
                        not _is_blacklisted_filename(filepath) and
                        _is_valid_extension(os.path.splitext(name)[1])):
                    all_files.append(filepath)

    return all_files
