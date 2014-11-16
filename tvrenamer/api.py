import logging
import os

from tvrenamer import episode
from tvrenamer import exceptions as exc

LOG = logging.getLogger(__name__)


class API(object):

    def __init__(self, locations=None):

        if locations and not isinstance(locations, list):
            locations = [locations]
        self.locations = locations if locations else []

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

        for location in self.locations:
            # if local path then make sure it is absolute
            if not location.startswith('\\'):
                location = os.path.abspath(os.path.expanduser(location))

            LOG.info('searching [%s]', location)
            for root, dirs, files in os.walk(location):
                LOG.debug('found file(s) %s', files)
                self.episodes.extend(
                    [episode.Episode(os.path.join(root, name))
                     for name in files])

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
                    ep.messages.append(str(err))
                ep.valid = False
                self.failed_episodes.append(ep)

        self.episodes[:] = [ep for ep in self.episodes if ep.valid]
        return any(self.episodes)

    @classmethod
    def execute(cls, locations):

        instance = cls(locations)

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
