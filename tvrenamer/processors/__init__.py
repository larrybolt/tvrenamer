"""Result processors plugins"""
from tvrenamer.processors import base


def load():
    """Load all processor plugins that are enabled.

    :returns: priority sorted processor plugins (high to low)
    :rtype: list
    """
    return base.EnabledExtensionManager()
