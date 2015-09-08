"""Regular expression patterns for filename formats.

Supported filename formats::

    * Sample.Show.S01E01.S01E02.S01E03.S01E04.eps.mp4
    * Sample-Show.S02e22e23e24.avi
    * Sample.Show.3x12.3x13.3x14.avi
    * Sample.Show.4x4x5x6.mp4
    * Sample.Show.S02E11-15-stuff.mkv
    * Sample-Show.2x11-15.avi
    * Sample-Show.[3x11-13].mp4
    * Sample.Show-[013].avi
    * Sample.S0202.mp4
    * Sample_Show-7x17.avi
    * Sample-Show S09.E11.mkv
    * Sample-Show S09_E11.mkv
    * Sample-Show S09 - E11.mkv
    * Sample_Show-[09.01].avi
    * Sample.Show - S9 E 9.avi
    * SampleShow - episode 1219 [S 13 - E 07].mkv
    * SampleShow - episode 1219 [S 13 Ep 07].avi
    * Sample Show 2 of 7.mp4
    * Sample.Show.Part.1.and.Part.2.avi
    * Sample.Show.pt.1 & pt 2 & pt.3.avi
    * Sample Show part 5.mkv
    * Sample.Show season 10 episode 15.mp4
    * Sample Show 909.mkv
    * Sample Show 1011.avi
    * Sample Show e19.mp4

"""
import re


# Patterns to parse input filenames with
FILENAME_PATTERNS = [
    # foo s01e23 s01e24 s01e25 *
    '''
    ^((?P<seriesname>.+?)[ \._\-])?          # show name
    [Ss](?P<seasonnumber>[0-9]+)             # s01
    [\.\- ]?                                 # separator
    [Ee](?P<episodenumberstart>[0-9]+)       # first e23
    ([\.\- ]+                                # separator
    [Ss](?P=seasonnumber)                    # s01
    [\.\- ]?                                 # separator
    [Ee][0-9]+)*                             # e24 etc (middle groups)
    ([\.\- ]+                                # separator
    [Ss](?P=seasonnumber)                    # last s01
    [\.\- ]?                                 # separator
    [Ee](?P<episodenumberend>[0-9]+))        # final episode number
    [^\/]*$
    ''',

    # foo.s01e23e24*
    '''
    ^((?P<seriesname>.+?)[ \._\-])?          # show name
    [Ss](?P<seasonnumber>[0-9]+)             # s01
    [\.\- ]?                                 # separator
    [Ee](?P<episodenumberstart>[0-9]+)       # first e23
    ([\.\- ]?                                # separator
    [Ee][0-9]+)*                             # e24e25 etc
    [\.\- ]?[Ee](?P<episodenumberend>[0-9]+) # final episode num
    [^\/]*$
    ''',

    # foo.1x23 1x24 1x25
    '''
    ^((?P<seriesname>.+?)[ \._\-])?          # show name
    (?P<seasonnumber>[0-9]+)                 # first season number (1)
    [xX](?P<episodenumberstart>[0-9]+)       # first episode (x23)
    ([ \._\-]+                               # separator
    (?P=seasonnumber)                        # more season numbers (1)
    [xX][0-9]+)*                             # more episode numbers (x24)
    ([ \._\-]+                               # separator
    (?P=seasonnumber)                        # last season number (1)
    [xX](?P<episodenumberend>[0-9]+))        # last episode number (x25)
    [^\/]*$
    ''',

    # foo.1x23x24*
    '''
    ^((?P<seriesname>.+?)[ \._\-])?          # show name
    (?P<seasonnumber>[0-9]+)                 # 1
    [xX](?P<episodenumberstart>[0-9]+)       # first x23
    ([xX][0-9]+)*                            # x24x25 etc
    [xX](?P<episodenumberend>[0-9]+)         # final episode num
    [^\/]*$
    ''',

    # foo.s01e23-24*
    '''
    ^((?P<seriesname>.+?)[ \._\-])?          # show name
    [Ss](?P<seasonnumber>[0-9]+)             # s01
    [\.\- ]?                                 # separator
    [Ee](?P<episodenumberstart>[0-9]+)       # first e23
    (                                        # -24 etc
         [\-]
         [Ee]?[0-9]+
    )*
         [\-]                                # separator
         [Ee]?(?P<episodenumberend>[0-9]+)   # final episode num
    [\.\- ]                                  # must have a separator (prevents s01e01-720p from being 720 episodes) # noqa
    [^\/]*$
    ''',

    # foo.1x23-24*
    '''
    ^((?P<seriesname>.+?)[ \._\-])?          # show name
    (?P<seasonnumber>[0-9]+)                 # 1
    [xX](?P<episodenumberstart>[0-9]+)       # first x23
    (                                        # -24 etc
         [\-+][0-9]+
    )*
         [\-+]                               # separator
         (?P<episodenumberend>[0-9]+)        # final episode num
    ([\.\-+ ].*                              # must have a separator (prevents 1x01-720p from being 720 episodes) # noqa
    |
    $)
    ''',

    # foo.[1x09-11]*
    '''
    ^(?P<seriesname>.+?)[ \._\-]          # show name and padding
    \[                                       # [
        ?(?P<seasonnumber>[0-9]+)            # season
    [xX]                                     # x
        (?P<episodenumberstart>[0-9]+)       # episode
        ([\-+] [0-9]+)*
    [\-+]                                    # -
        (?P<episodenumberend>[0-9]+)         # episode
    \]                                       # \]
    [^\\/]*$
    ''',

    # foo - [012]
    '''
    ^((?P<seriesname>.+?)[ \._\-])?       # show name and padding
    \[                                       # [ not optional (or too ambigious) # noqa
    (?P<episodenumber>[0-9]+)                # episode
    \]                                       # ]
    [^\\/]*$
    ''',

    # foo.s0101, foo.S0201
    '''
    ^(?P<seriesname>.+?)[ \._\-]
    [Ss](?P<seasonnumber>[0-9]{2})
    [\.\- ]?
    (?P<episodenumber>[0-9]{2})
    [^0-9]*$
    ''',

    # foo.1x09*
    '''
    ^((?P<seriesname>.+?)[ \._\-])?       # show name and padding
    \[?                                      # [ optional
    (?P<seasonnumber>[0-9]+)                 # season
    [xX]                                     # x
    (?P<episodenumber>[0-9]+)                # episode
    \]?                                      # ] optional
    [^\\/]*$
    ''',

    # foo.s01.e01, foo.s01_e01, "foo.s01 - e01"
    '''
    ^((?P<seriesname>.+?)[ \._\-])?
    \[?
    [Ss](?P<seasonnumber>[0-9]+)[ ]?[\._\- ]?[ ]?
    [Ee]?(?P<episodenumber>[0-9]+)
    \]?
    [^\\/]*$
    ''',

    # foo - [01.09]
    '''
    ^((?P<seriesname>.+?))                # show name
    [ \._\-]?                                # padding
    \[                                       # [
    (?P<seasonnumber>[0-9]+?)                # season
    [.]                                      # .
    (?P<episodenumber>[0-9]+?)               # episode
    \]                                       # ]
    [ \._\-]?                                # padding
    [^\\/]*$
    ''',

    # Foo - S2 E 02 - etc
    '''
    ^(?P<seriesname>.+?)[ ]?[ \._\-][ ]?
    [Ss](?P<seasonnumber>[0-9]+)[\.\- ]?
    [Ee]?[ ]?(?P<episodenumber>[0-9]+)
    [^\\/]*$
    ''',

    # Show - Episode 9999 [S 12 - Ep 131] - etc
    '''
    (?P<seriesname>.+)                       # Showname
    [ ]-[ ]                                  # -
    [Ee]pisode[ ]\d+                         # Episode 1234 (ignored)
    [ ]
    \[                                       # [
    [sS][ ]?(?P<seasonnumber>\d+)            # s 12
    ([ ]|[ ]-[ ]|-)                          # space, or -
    ([eE]|[eE]p)[ ]?(?P<episodenumber>\d+)   # e or ep 12
    \]                                       # ]
    .*$                                      # rest of file
    ''',

    # show name 2 of 6 - blah
    '''
    ^(?P<seriesname>.+?)                  # Show name
    [ \._\-]                                 # Padding
    (?P<episodenumber>[0-9]+)                # 2
    [ \._\-]?                                # Padding
    of                                       # of
    [ \._\-]?                                # Padding
    \d+                                      # 6
    ([\._ -]|$|[^\\/]*$)                     # More padding, then anything
    ''',

    # Show.Name.Part.1.and.Part.2
    '''
    ^(?i)
    (?P<seriesname>.+?)                        # Show name
    [ \._\-]                                   # Padding
    (?:part|pt)?[\._ -]
    (?P<episodenumberstart>[0-9]+)             # Part 1
    (?:
      [ \._-](?:and|&|to)                        # and
      [ \._-](?:part|pt)?                        # Part 2
      [ \._-](?:[0-9]+))*                        # (middle group, optional, repeating) # noqa
    [ \._-](?:and|&|to)                        # and
    [ \._-]?(?:part|pt)?                       # Part 3
    [ \._-](?P<episodenumberend>[0-9]+)        # last episode number, save it
    [\._ -][^\\/]*$                            # More padding, then anything
    ''',

    # Show.Name.Part1
    '''
    ^(?P<seriesname>.+?)                  # Show name\n
    [ \\._\\-]                               # Padding\n
    [Pp]art[ ](?P<episodenumber>[0-9]+)      # Part 1\n
    [\\._ -][^\\/]*$                         # More padding, then anything\n
    ''',

    # show name Season 01 Episode 20
    '''
    ^(?P<seriesname>.+?)[ ]?               # Show name
    [Ss]eason[ ]?(?P<seasonnumber>[0-9]+)[ ]? # Season 1
    [Ee]pisode[ ]?(?P<episodenumber>[0-9]+)   # Episode 20
    [^\\/]*$                                # Anything
    ''',

    # foo.103*
    '''
    ^(?P<seriesname>.+)[ \._\-]
    (?P<seasonnumber>[0-9]{1})
    (?P<episodenumber>[0-9]{2})
    [\._ -][^\\/]*$
    ''',

    # foo.0103*
    '''
    ^(?P<seriesname>.+)[ \._\-]
    (?P<seasonnumber>[0-9]{2})
    (?P<episodenumber>[0-9]{2,3})
    [\._ -][^\\/]*$
    ''',

    # show.name.e123.abc
    '''
    ^(?P<seriesname>.+?)                  # Show name
    [ \._\-]                                 # Padding
    [Ee](?P<episodenumber>[0-9]+)            # E123
    [\._ -][^\\/]*$                          # More padding, then anything
    ''',
]

_EXPRESSIONS = []


def get_expressions():
    """Retrieve compiled pattern expressions.

    :returns: compiled regular expressions for supported filename formats
    :rtype: list
    """

    if len(_EXPRESSIONS) == len(FILENAME_PATTERNS):
        return _EXPRESSIONS

    for cpattern in FILENAME_PATTERNS:
        _EXPRESSIONS.append(re.compile(cpattern, re.VERBOSE))
    return _EXPRESSIONS


# pre-load the regular expressions to avoid race condition
# when multiple threads attempt to reference them.
get_expressions()
