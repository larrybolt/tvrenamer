import copy
import functools
import itertools
import logging
import os
import re

import six

LOG = logging.getLogger(__name__)


def make_opt_list(opts, group):
    """Generate a list of tuple containing group, options

    :param opts: option lists associated with a group
    :type opts: list
    :param group: name of an option group
    :type group: str
    :return: a list of (group_name, opts) tuples
    :rtype: list
    """
    _opts = [(group, list(itertools.chain(*opts)))]
    return [(g, copy.deepcopy(o)) for g, o in _opts]


def apply_replacements(cfile, replacements):
    """Applies custom replacements.

    mapping(dict), where each dict contains:
        'match' - filename match pattern to check against, the filename
        replacement is applied.

        'replacement' - string used to replace the matched part of the filename

        'is_regex' - if True, the pattern is treated as a
        regex. If False, simple substring check is used (if
        'match' in filename). Default is False

        'with_extension' - if True, the file extension is not included in the
        pattern matching. Default is False

    Example replacements::

        {'match': ':',
         'replacement': '-',
         'is_regex': False,
         'with_extension': False,
         }

    :param str cfile: name of a file
    :param list replacements: mapping(dict) filename pattern matching
                              directives
    :returns: formatted filename
    :rtype: str
    """
    if not replacements:
        return cfile

    for rep in replacements:
        if not rep.get('with_extension', False):
            # By default, preserve extension
            cfile, cext = os.path.splitext(cfile)
        else:
            cfile = cfile
            cext = ''

        if 'is_regex' in rep and rep['is_regex']:
            cfile = re.sub(rep['match'], rep['replacement'], cfile)
        else:
            cfile = cfile.replace(rep['match'], rep['replacement'])

        # Rejoin extension (cext might be empty-string)
        cfile = cfile + cext

    return cfile


def is_valid_extension(extension, valid_extensions):
    """Checks if the file extension is blacklisted in valid_extensions.

    :param str extension: a file extension to check
    :param list valid_extensions: a list of file extensions considered valid
    :returns: flag indicating if the extension is valid based on list of
              valid extensions.
    :rtype: bool
    """
    if not valid_extensions:
        return True

    for cext in valid_extensions:
        if not cext.startswith('.'):
            cext = '.%s' % cext
        if extension == cext:
            return True
    else:
        return False


def is_blacklisted_filename(filepath, filename, filename_blacklist):
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
    :param str filename: name of a file to check against the blacklist
    :param list filename_blacklist: filename(s) or a mapping(dict) for
                                    matching file patterns.
    :returns: flag indicating if the file was matched in the blacklist
    :rtype: bool
    """

    if not filename_blacklist:
        return False

    fname, fext = os.path.splitext(filename)

    for fblacklist in filename_blacklist:
        if isinstance(fblacklist, six.string_types):
            if filename == fblacklist:
                return True
            continue  # pragma: no cover

        if fblacklist.get('full_path'):
            to_check = filepath
        else:
            if fblacklist.get('exclude_extension', False):
                to_check = fname
            else:
                to_check = filename

        if fblacklist.get('is_regex', False):
            if re.match(fblacklist['match'], to_check) is not None:
                return True
        else:
            if fblacklist['match'] in to_check:
                return True
    else:
        return False


def retrieve_files(locations):
    """Get list of files found in provided locations.

    Search through the paths provided to find files for processing.

    :param list locations: directories to search
    :returns: absolute path of filename
    :rtype: list
    """

    all_files = []
    for location in locations:
        # if local path then make sure it is absolute
        if not location.startswith('\\'):
            location = os.path.abspath(os.path.expanduser(location))

        LOG.debug('searching [%s]', location)
        for root, dirs, files in os.walk(location):
            LOG.debug('found file(s) %s', files)
            all_files.extend([os.path.join(root, name) for name in files])

    return all_files


def find_library(series_path, locations, default_location):
    """Search for the location of a series within the library.

    :param str series_path: name of the relative path of the series
    :param list locations: root path of media libraries
    :param str default_location: root path of the default media library
    """

    for location in locations:
        if os.path.isdir(os.path.join(location, series_path)):
            return location
        # already tried the full path; now walk down the path
        segments = series_path.split(os.sep)[:-1]
        while segments:
            seg_path = os.path.join(*segments)
            # if the directory exists then we found our location
            if os.path.isdir(os.path.join(location, seg_path)):
                return location
            # remove the last element and try again
            segments = segments[:-1]

    return default_location


def state(method=None, pre=None, post=None, attr='state'):
    """State decorator"""

    # if called without method, it means we have been called with
    # optional arguments, we return a decorator with optional arguments
    # filled in. Next time around we'll be decorating
    if method is None:
        return functools.partial(state, pre=pre, post=post, attr=attr)

    # functools makes sure that we don't lose the method details
    # like method name or doc.
    @functools.wraps(method)
    def inner(self, *args, **kwargs):
        """Inner wrapper for apply pre/post states"""
        if pre is not None:
            setattr(self, attr, pre)
        result = method(self, *args, **kwargs)
        if post is not None:
            setattr(self, attr, post)
        return result
    return inner
