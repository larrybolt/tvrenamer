from tvrenamer.processors import base


class NoopResults(base.ResultProcessorBase):
    """Result processor that does nothing."""

    @property
    def priority(self):
        """Processor priority used for sorting to determine execution order."""
        return 1

    @property
    def enabled(self):
        """Determines if a processor plugin is enabled for processing data."""
        return True

    def process(self, data):
        """Process the results from episode processing.

        :param list data: result instances
        """
