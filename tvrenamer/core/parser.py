from tvrenamer.core import patterns


def _get_season_no(match, namedgroups):
    if 'seasonnumber' in namedgroups:
        return int(match.group('seasonnumber'))
    return 1


def _get_episode_by_boundary(match):

    # Multiple episodes, regex specifies start and end number
    start = int(match.group('episodenumberstart'))
    end = int(match.group('episodenumberend'))
    if start > end:
        # Swap start and end
        start, end = end, start
    return list(range(start, end + 1))


def _get_episodes(match, namedgroups):

    if 'episodenumberstart' in namedgroups:
        return _get_episode_by_boundary(match)
    else:
        return [int(match.group('episodenumber')), ]


def parse_filename(filename):
    """Parse media filename for metadata.

    :param str filename: the name of media file
    :returns: dict of metadata attributes found in filename
              or None if no matching expression.
    :rtype: dict
    """

    _patterns = patterns.get_expressions()

    for cmatcher in _patterns:
        match = cmatcher.match(filename)
        if match:
            namedgroups = match.groupdict().keys()

            result = {}
            result['pattern'] = cmatcher.pattern
            result['series_name'] = match.group('seriesname')
            result['season_number'] = _get_season_no(match, namedgroups)
            result['episode_numbers'] = _get_episodes(match, namedgroups)
            return result
    else:
        return None
