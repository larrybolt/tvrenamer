from tvrenamer.processors import base


class NoopResults(base.ResultProcessorBase):
    """Result processor that does nothing."""

    def process(self, data):
        """Process the results from episode processing.

        :param list data: result instances
        """
