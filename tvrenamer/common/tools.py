import copy
import itertools
import re
import warnings

import six

# Pattern for splitting filenames into basename and extension.
# Useful for matching subtitles with language codes, for example
# "extension_pattern": "(\.(eng|cze))?(\.[a-zA-Z0-9]+)$" will split
# "foo.eng.srt" into "foo" and ".eng.srt".
# Note that extensions still pass 'valid_extensions' filter,
# '.eng.srt' passes when 'srt' is specified in 'valid_extensions'.
EXTENSION_PATTERN = '(\.[a-zA-Z0-9]+)$'


def print_out(msg, end=None):
    """
    Print to sys.stdout a message
    """
    six.print_(msg.encode('utf-8'), end=end)


def warn(text, logger=None):
    """Displays message to sys.stderr
    """
    if logger:
        logger.warning(text)
    warnings.warn(str(text), RuntimeWarning, stacklevel=2)


def make_opt_list(opts, group):
    """
    Generate a list of tuple containing group, options
    :param opts: option lists associated with a group
    :type opts: list
    :param group: name of an option group
    :type group: str
    :return: a list of (group_name, opts) tuples
    :rtype: list
    """
    _opts = [(group, list(itertools.chain(*opts)))]
    return [(g, copy.deepcopy(o)) for g, o in _opts]


def split_extension(filename):

    # Pattern for splitting filenames into basename and extension.
    # Useful for matching subtitles with language codes, for example
    # "extension_pattern": "(\.(eng|cze))?(\.[a-zA-Z0-9]+)$" will split
    # "foo.eng.srt" into "foo" and ".eng.srt".
    # Note that extensions still pass 'valid_extensions' filter,
    # '.eng.srt' passes when 'srt' is specified in 'valid_extensions'.
    base = re.sub(EXTENSION_PATTERN, '', filename)
    ext = filename.replace(base, '')
    return base, ext


def apply_replacements(cfile, replacements):
    """Applies custom replacements.

    :param str cfile: name of a file
    :param list replacements: mapping(dict) of 'match', 'replacement',
                              and 'is_regex' (optional)
    """
    if not replacements:
        return cfile

    for rep in replacements:
        if not rep.get('with_extension', False):
            # By default, preserve extension
            cfile, cext = split_extension(cfile)
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
    """Checks if the file extension is blacklisted in valid_extensions
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
    """Checks if the filename (optionally excluding extension)
    matches filename_blacklist

    with_blacklist should be a list of strings and/or dicts:

    a string, specifying an exact filename to ignore
    "filename_blacklist": [".DS_Store", "Thumbs.db"],

    a dictionary, where each dict contains:

    Key 'match' - (if the filename matches the pattern, the filename
    is blacklisted)

    Key 'is_regex' - if True, the pattern is treated as a
    regex. If False, simple substring check is used (if
    cur['match'] in filename). Default is False

    Key 'full_path' - if True, full path is checked. If False, only
    filename is checked. Default is False.

    Key 'exclude_extension' - if True, the extension is removed
    from the file before checking. Default is False.
    """

    if not filename_blacklist:
        return False

    fname, fext = split_extension(filename)

    for fblacklist in filename_blacklist:
        if isinstance(fblacklist, six.string_types):
            if filename == fblacklist:
                return True
            else:
                continue

        if fblacklist.get('full_path'):
            to_check = filepath
        else:
            if fblacklist.get('exclude_extension', False):
                to_check = fname
            else:
                to_check = filename

        if fblacklist.get('is_regex', False):
            m = re.match(fblacklist['match'], to_check)
            if m is not None:
                return True
        else:
            m = fblacklist['match'] in to_check
            if m:
                return True
    else:
        return False
