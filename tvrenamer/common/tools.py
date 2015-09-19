import copy
import itertools


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
