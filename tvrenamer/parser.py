import logging
import re

from tvrenamer import patterns

LOG = logging.getLogger(__name__)


def _get_series_name(match, namedgroups):
    if 'seriesname' in namedgroups:
        return match.group('seriesname')
    return None


def _get_season_no(match, namedgroups):
    if 'seasonnumber' in namedgroups:
        return int(match.group('seasonnumber'))
    return 1


def _get_extra_values(match):
    extra_values = match.groupdict()
    if extra_values is None:
        extra_values = {}
    return extra_values


def _get_episode_by_listed(match, namedgroups):
    # Multiple episodes, have episodenumber1 or 2 etc
    episode_numbers = []
    for cur in namedgroups:
        epnomatch = re.match('episodenumber(\d+)', cur)
        if epnomatch:
            episode_numbers.append(int(match.group(cur)))
    episode_numbers.sort()
    return episode_numbers


def _get_episode_by_boundary(match):

    # Multiple episodes, regex specifies start and end number
    start = int(match.group('episodenumberstart'))
    end = int(match.group('episodenumberend'))
    if end - start > 5:
        LOG.warning('%s episodes detected in file confused by numeric '
                    'episode name, using first match: %s', end - start, start)
        return [start]
    elif start > end:
        # Swap start and end
        start, end = end, start
        return range(start, end + 1)
    else:
        return range(start, end + 1)


def _get_episodes(match, namedgroups):

    if 'episodenumber1' in namedgroups:
        return _get_episode_by_listed(match, namedgroups)
    elif 'episodenumberstart' in namedgroups:
        return _get_episode_by_boundary(match)
    elif 'episodenumber' in namedgroups:
        return [int(match.group('episodenumber')), ]
    else:
        return None


def parse_filename(filename):

    _patterns = patterns.get_expressions(LOG)

    for cmatcher in _patterns:
        match = cmatcher.match(filename)
        if match:
            namedgroups = match.groupdict().keys()

            result = {}
            result['pattern'] = cmatcher.pattern
            result['series_name'] = _get_series_name(match, namedgroups)
            result['season_number'] = _get_season_no(match, namedgroups)
            result['extra_values'] = _get_extra_values(match)
            result['episode_numbers'] = _get_episodes(match, namedgroups)
            return result
    else:
        return None
