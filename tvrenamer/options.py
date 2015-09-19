from oslo_config import cfg

import tvrenamer


DEFAULT_LOG_FILENAME = '{0}.log'.format(tvrenamer.PROJECT_NAME)
DEFAULT_LOG_LEVEL = 'info'

CLI_OPTS = [
    cfg.MultiStrOpt('locations',
                    positional=True,
                    help='specify the paths to search for files to rename.'),
    cfg.BoolOpt('dryrun',
                default=False,
                help='Practice run where no changes are applied.'),
    cfg.BoolOpt('cron',
                default=False,
                help='Disable console output when running via cron'),
    cfg.BoolOpt('cache_enabled',
                default=False,
                help='Enable caching results'),
    cfg.StrOpt('logfile',
               metavar='LOG_FILE',
               default=DEFAULT_LOG_FILENAME,
               help='specify name of log file default: %(default)s'),
    cfg.StrOpt('loglevel',
               metavar='LOG_LEVEL',
               default=DEFAULT_LOG_LEVEL,
               help='specify logging level to log messages: %(choices)s',
               choices=['none',
                        'critical',
                        'error',
                        'warning',
                        'info',
                        'debug',
                        'trace']),
]

EPISODE_OPTS = [
    cfg.BoolOpt('move_files_enabled',
                default=False,
                help='Move files to library during rename.'),
    cfg.BoolOpt('overwrite_file_enabled',
                default=False,
                help='Overwrite existing files during rename.'),
    cfg.StrOpt('default_library',
               default='',
               help='Default library path to relocate files to.'),
    cfg.ListOpt('libraries',
                default=[],
                help='Library paths to relocate files to.'),
    cfg.StrOpt('language',
               default='en',
               help='Lanuage to lookup metadata in.'),
    cfg.ListOpt('valid_extensions',
                default=[],
                help='File extensions considered valid.'),
    cfg.ListOpt('filename_blacklist',
                default=[],
                help='File names exclused from processing.'),
    cfg.ListOpt('input_filename_replacements',
                default=[],
                help='List of mappings of string pattern replacements.'),
    cfg.DictOpt('input_series_replacements',
                default={},
                help='Mapping of parsed series name to replacement values.'),
    cfg.DictOpt('output_series_replacements',
                default={},
                help='Mapping of lookup series name to replacement values.'),
    cfg.StrOpt('lookup_service',
               default='tvdb',
               help='Name of lookup service to use for metadata retrieval.'),
]

FORMAT_OPTS = [
    # Destination to move files to. Trailing slash is not necessary.
    # Use forward slashes, even on Windows. Realtive paths are realtive to
    # the existing file's path (not current working dir). A value of '.' will
    # not move the file anywhere.
    #
    # Use Python's string formatting to add dynamic paths. Available variables:
    # - %(seriesname)s
    # - %(seasonnumber)d
    # - %(episodenumbers)s (Note: this is a string, formatted with config
    #                       variable episode_single and joined with
    #                       episode_separator)
    cfg.StrOpt('directory_name_format',
               default='.',
               help='Format for naming library directories.'),
    cfg.StrOpt('filename_format_ep',
               default='%(seriesname)s - %(seasonnumber)02dx%(episode)s - %(episodename)s%(ext)s',  # noqa
               help='Format for naming files with episode name.'),
    cfg.StrOpt('episode_single',
               default='%02d',
               help='Format for episode numbers.'),
    cfg.StrOpt('episode_separator',
               default='-',
               help='Separator to join multiple episode numbers.'),
    cfg.StrOpt('multiep_join_name_with',
               default=', ',
               help='Separator to join multiple episodes.'),
    cfg.StrOpt('multiep_format',
               default='%(epname)s (%(episodemin)s-%(episodemax)s)',
               help='Format for naming multiple episodes.'),
    cfg.StrOpt('filename_character_blacklist',
               default='',
               help='Characters to ignore within filename.'),
    cfg.StrOpt('replacement_character',
               default='_',
               help='Character used to replace invalid characters.'),
    cfg.ListOpt('output_filename_replacements',
                default=[],
                help='List of mappings of string pattern replacements.'),
]

CACHE_OPTS = [
    cfg.StrOpt('connection',
               default='sqlite:///$config_dir/cache.db',
               help='The connection string used to connect to the database'),
    cfg.IntOpt('idle_timeout',
               default=3600,
               help='Timeout before idle sql connections are reaped'),
    cfg.IntOpt('connection_debug',
               default=0,
               help='Verbosity of SQL debugging information. 0=None, 100=All'),
]


def register_opts(conf):
    """Configure options within configuration library."""
    conf.register_cli_opts(CLI_OPTS)
    conf.register_opts(EPISODE_OPTS)
    conf.register_opts(FORMAT_OPTS)
    conf.register_opts(CACHE_OPTS, 'cache')


def list_opts():
    """Returns a list of oslo_config options available in the library.

    The returned list includes all oslo_config options which may be registered
    at runtime by the library.
    Each element of the list is a tuple. The first element is the name of the
    group under which the list of elements in the second element will be
    registered. A group name of None corresponds to the [DEFAULT] group in
    config files.
    The purpose of this is to allow tools like the Oslo sample config file
    generator to discover the options exposed to users by this library.

    :returns: a list of (group_name, opts) tuples
    """
    from tvrenamer.common import tools
    all_opts = []
    all_opts.extend(tools.make_opt_list([CLI_OPTS,
                                         EPISODE_OPTS,
                                         FORMAT_OPTS], None))
    all_opts.extend(tools.make_opt_list([CACHE_OPTS], 'cache'))
    return all_opts
