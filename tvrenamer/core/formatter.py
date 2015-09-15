import os
import platform
import re

from oslo_config import cfg
import six
import titlecase as tc

from tvrenamer.common import encodeutils

tc.ALL_CAPS = re.compile(r'^[A-Z\s%s]+$' % tc.PUNCT)


def _replace_series_name(seriesname, replacements):
    """Performs replacement of series name.

    Allow specified replacements of series names in cases where default
    filenames match the wrong series, e.g. missing year gives wrong answer,
    or vice versa. This helps the TVDB query get the right match.
    """
    for pat, replacement in six.iteritems(replacements):
        if re.match(pat, seriesname, re.IGNORECASE | re.UNICODE):
            return replacement
    return seriesname


def clean_series_name(seriesname):
    """Cleans up series name.

    By removing any . and _ characters, along with any trailing hyphens.

    Is basically equivalent to replacing all _ and . with a
    space, but handles decimal numbers in string, for example:

    >>> _clean_series_name("an.example.1.0.test")
    'an example 1.0 test'
    >>> _clean_series_name("an_example_1.0_test")
    'an example 1.0 test'
    """
    if not seriesname:
        return seriesname
    # TODO(xxxx): Could this be made to clean "Hawaii.Five-0.2010" into
    # "Hawaii Five-0 2010"?
    seriesname = re.sub('(\D)[.](\D)', '\\1 \\2', seriesname)
    seriesname = re.sub('(\D)[.]', '\\1 ', seriesname)
    seriesname = re.sub('[.](\D)', ' \\1', seriesname)
    seriesname = seriesname.replace('_', ' ')
    seriesname = re.sub('-$', '', seriesname)
    return _replace_series_name(seriesname.strip(),
                                cfg.CONF.input_series_replacements)


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


def _format_episode_numbers(episodenumbers):
    """Format episode number(s) into string, using configured values."""
    if len(episodenumbers) == 1:
        epno = cfg.CONF.episode_single % episodenumbers[0]
    else:
        epno = cfg.CONF.episode_separator.join(
            cfg.CONF.episode_single % x for x in episodenumbers)

    return epno


def _format_episode_name(names):
    """Takes a list of episode names, formats them into a string.

    If two names are supplied, such as "Pilot (1)" and "Pilot (2)", the
    returned string will be "Pilot (1-2)". Note that the first number
    is not required, for example passing "Pilot" and "Pilot (2)" will
    also result in returning "Pilot (1-2)".

    If two different episode names are found, such as "The first", and
    "Something else" it will return "The first, Something else"
    """
    if len(names) == 1:
        return names[0]

    found_name = ''
    epname = None
    epno = None
    numbers = []
    for cname in names:
        match = re.match('(.*) \(([0-9]+)\)$', cname)
        if found_name != '' and (not match or epname != found_name):
            # An episode didn't match
            return cfg.CONF.multiep_join_name_with.join(names)

        if match:
            epname, epno = match.group(1), match.group(2)
        else:  # assume that this is the first episode, without number
            epname = cname
            epno = 1
        found_name = epname
        numbers.append(int(epno))

    return cfg.CONF.multiep_format % {'epname': found_name,
                                      'episodemin': min(numbers),
                                      'episodemax': max(numbers)}


def _make_valid_filename(value):
    """Takes a string and makes it into a valid filename.

    replaces accented characters with ASCII equivalent, and
    removes characters that cannot be converted sensibly to ASCII.

    additional characters that will removed. This
    will not touch the extension separator:

        >>> _make_valid_filename("T.est.avi")
        'T_est.avi'
    """

    sysname = platform.system()

    # If the filename starts with a . prepend it with an underscore, so it
    # doesn't become hidden.
    # This is done before calling splitext to handle filename of ".", as
    # splitext acts differently in python 2.5 and 2.6 - 2.5 returns ('', '.')
    # and 2.6 returns ('.', ''), so rather than special case '.', this
    # special-cases all files starting with "." equally (since dotfiles have
    # no extension)
    if value.startswith('.'):
        value = cfg.CONF.replacement_character + value

    # Treat extension seperatly
    value, extension = os.path.splitext(value)

    # Remove any null bytes
    value = value.replace('\0', '')

    # Blacklist of characters
    if sysname == 'Darwin':
        # : is technically allowed, but Finder will treat it as / and will
        # generally cause weird behaviour, so treat it as invalid.
        blacklist = r'/:'
    elif sysname in ['Linux', 'FreeBSD']:
        blacklist = r'/'
    else:
        # platform.system docs say it could also return "Windows" or "Java".
        # Failsafe and use Windows sanitisation for Java, as it could be any
        # operating system.
        blacklist = r'\/:*?\"<>|'

    # Append custom blacklisted characters
    blacklist += cfg.CONF.filename_character_blacklist

    # Replace every blacklisted character with a underscore
    value = re.sub('[%s]' % re.escape(blacklist),
                   cfg.CONF.replacement_character, value)

    # Remove any trailing whitespace
    value = value.strip()

    # There are a bunch of filenames that are not allowed on Windows.
    # As with character blacklist, treat non Darwin/Linux platforms as Windows
    if sysname not in ['Darwin', 'Linux']:
        invalid_filenames = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2',
                             'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8',
                             'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5',
                             'LPT6', 'LPT7', 'LPT8', 'LPT9']
        if value in invalid_filenames:
            value = cfg.CONF.replacement_character + value

    # Replace accented characters with ASCII equivalent
    value = encodeutils.safe_encode(value, encoding='ascii', errors='ignore')
    extension = encodeutils.safe_encode(extension, encoding='ascii',
                                        errors='ignore')

    # Truncate filenames to valid/sane length.
    # NTFS is limited to 255 characters, HFS+ and EXT3 don't seem to have
    # limits, FAT32 is 254. I doubt anyone will take issue with losing that
    # one possible character, and files over 254 are pointlessly unweidly
    max_len = 254

    if len(value + extension) > max_len:
        if len(extension) > len(value):
            # Truncate extension instead of filename, no extension should be
            # this long..
            new_length = max_len - len(value)
            extension = extension[:new_length]
        else:
            # File name is longer than extension, truncate filename.
            new_length = max_len - len(extension)
            value = value[:new_length]

    return encodeutils.safe_decode(value + extension, incoming='ascii')


def format_filename(series_name, season_number,
                    episode_numbers, episode_names,
                    extension):
    """Generates a filename based on metadata using configured format.

    :param str series_name: name of TV series
    :param int season_number: the numeric season of series
    :param list(int) episode_numbers: the numeric episode of the series
    :param list(str) episode_names: episode title of the series
    :param str extension: media file extension
    :returns: formatted filename using input values and configured format
    :rtype: str
    """

    epdata = {
        'seriesname': tc.titlecase(_replace_series_name(
            series_name, cfg.CONF.output_series_replacements) or ''),
        'seasonnumber': season_number,
        'episode': _format_episode_numbers(episode_numbers),
        'episodename': tc.titlecase(_format_episode_name(episode_names)),
        'ext': extension,
        }

    value = apply_replacements(
        cfg.CONF.filename_format_ep % epdata,
        cfg.CONF.output_filename_replacements)

    return _make_valid_filename(value)


def format_dirname(series_name, season_number):
    """Generates a directory name based on metadata using configured format.

    :param str series_name: name of TV series
    :param int season_number: the numeric season of series
    :returns: formatted directory name using input values and configured format
    :rtype: str
    """

    data = {
        'seriesname': _replace_series_name(
            series_name, cfg.CONF.output_series_replacements),
        'seasonnumber': season_number,
        }

    return tc.titlecase(cfg.CONF.directory_name_format % data)


def find_library(series_path):
    """Search for the location of a series within the library.

    :param str series_path: name of the relative path of the series
    :returns: library path
    :rtype: str
    """

    for location in cfg.CONF.libraries:
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

    return cfg.CONF.default_library


def format_location(series_name, season_number):
    dirname = format_dirname(series_name, season_number)
    return os.path.join(find_library(dirname), dirname)
