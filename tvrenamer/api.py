import logging

from oslo.config import cfg

from tvrenamer.common import tools
from tvrenamer.core import episode
from tvrenamer import exceptions as exc
from tvrenamer import service

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('locations', 'tvrenamer.options')


class API(object):

    def __init__(self):
        service.prepare_service()
        self.locations = cfg.CONF.locations
        self.episodes = []
        self.failed_episodes = []

    def add_locations(self, locations):
        if isinstance(locations, list):
            self.locations.extend(locations)
        else:
            self.locations.append(locations)

    def get_results(self):
        results = dict()

        for ep in self.episodes:
            results[ep.original] = {
                'formatted_filename': ep.formatted_filename,
                'result': True,
                'messages': None,
                }

        for ep in self.failed_episodes:
            results[ep.original] = {
                'formatted_filename': ep.formatted_filename,
                'result': False,
                'messages': '\n\t'.join(ep.messages),
                }

        return results

    def find_files(self):

        for file in tools.retrieve_files(self.locations, LOG):
            self.episodes.append(episode.Episode(file))
        return any(self.episodes)

    def valid_files(self):

        for ep in self.episodes:
            LOG.debug('validating %s', ep)
            if not ep.valid:
                self.failed_episodes.append(ep)
        self.episodes[:] = [ep for ep in self.episodes if ep.valid]
        return any(self.episodes)

    def parse_files(self):

        for ep in self.episodes:
            LOG.debug('parsing %s', ep)
            try:
                ep.parse()
            except Exception as err:
                if not isinstance(err, exc.BaseTvRenamerException):
                    LOG.exception('parse_file exception occurred')
                    ep.messages.append(str(err))
                ep.valid = False
                self.failed_episodes.append(ep)

        self.episodes[:] = [ep for ep in self.episodes if ep.valid]
        return any(self.episodes)

    def enhance_files(self):

        for ep in self.episodes:
            LOG.debug('enhancing %s', ep)
            try:
                ep.enhance()
            except Exception as err:
                if not isinstance(err, exc.BaseTvRenamerException):
                    LOG.exception('enhance_files exception occurred')
                    ep.messages.append(str(err))
                ep.valid = False
                self.failed_episodes.append(ep)

        self.episodes[:] = [ep for ep in self.episodes if ep.valid]
        return any(self.episodes)

    def rename_files(self):

        for ep in self.episodes:
            LOG.debug('renaming %s', ep)
            try:
                ep.execute_rename()
            except Exception as err:
                if not isinstance(err, exc.BaseTvRenamerException):
                    LOG.exception('rename_files exception occurred')
                    ep.messages.append(str(err))
                ep.valid = False
                self.failed_episodes.append(ep)

        self.episodes[:] = [ep for ep in self.episodes if ep.valid]
        return any(self.episodes)

    @classmethod
    def execute(cls):

        instance = cls()

        if not instance.find_files():
            return instance.get_results()

        if not instance.valid_files():
            return instance.get_results()

        if not instance.parse_files():
            return instance.get_results()

        if not instance.enhance_files():
            return instance.get_results()

        if not instance.rename_files():
            return instance.get_results()

        return instance.get_results()
