"""Provides the base result processor abstract class."""
import abc

import six
from stevedore import enabled

RESULTS_NAMESPACE = 'tvrenamer.results.processors'


class EnabledExtensionManager(enabled.EnabledExtensionManager):
    """Extends stevedore.enabled.EnabledExtensionManaer.

        Provides default inputs for the manager.
    """

    def __init__(self):

        def check_enabled(ext):
            """Check if extension is enabled."""
            return ext.obj.enabled

        super(EnabledExtensionManager, self).__init__(
            namespace=RESULTS_NAMESPACE,
            check_func=check_enabled,
            invoke_on_load=True
        )

    def sorted_extensions(self):
        return sorted(self.extensions,
                      key=lambda x: x.obj.priority,
                      reverse=True)

    def map(self, func, *args, **kwds):
        response = []
        for e in self.sorted_extensions():
            self._invoke_one_plugin(response.append, func, e, args, kwds)
        return response


@six.add_metaclass(abc.ABCMeta)
class ResultProcessorBase(object):
    """Abstract class that provides the structure of a result processor."""

    @property
    def priority(self):
        """Processor priority used for sorting to determine execution order."""
        return 1

    @property
    def enabled(self):
        """Determines if a processor plugin is enabled for processing data."""
        return True

    @abc.abstractmethod
    def process(self, data):
        """Process the results from episode processing.

        :param list data: result instances
        """
        raise NotImplementedError
