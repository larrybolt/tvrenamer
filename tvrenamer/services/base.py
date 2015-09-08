import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Service(object):

    @abc.abstractmethod
    def get_series_by_name(self, series_name):
        """Perform lookup for series

        :param str series_name: series name found within filename
        :returns: instance of series
        :rtype: object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_series_by_id(self, series_id):
        """Perform lookup for series

        :param int series_id: series id of series
        :returns: instance of series
        :rtype: object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_series_name(self, series):
        """Perform lookup for name of series

        :param object series: instance of a series
        :returns: name of series
        :rtype: str
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_episode_name(self, series, episode_numbers, season_number):
        """Perform lookup for name of episode numbers for a given series.

        :param object series: instance of a series
        :param list episode_numbers: the episode sequence number
        :param int season_number: numeric season of series
        :returns: list of episode name
        :rtype: list(str)
        """
        raise NotImplementedError
