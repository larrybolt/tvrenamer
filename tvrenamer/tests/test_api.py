import os

import mock

from tvrenamer import api
from tvrenamer.core import episode
from tvrenamer import services
from tvrenamer.tests import base


class ApiTest(base.BaseTest):

    def test_init(self):

        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            self.assertEqual(myapi.episodes, [])
            self.assertEqual(myapi.failed_episodes, [])
            self.assertEqual(myapi.locations, [])

        with mock.patch.object(api.service, 'prepare_service'):
            self.CONF.set_override(
                'locations',
                ['/tmp/tvshows', '/tmp/download/shows'])

            myapi = api.API()
            self.assertEqual(myapi.episodes, [])
            self.assertEqual(myapi.failed_episodes, [])
            self.assertEqual(myapi.locations,
                             ['/tmp/tvshows',
                              '/tmp/download/shows'])

    def test_add_locations(self):
        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            myapi.add_locations('/tmp/tvshows')
            self.assertEqual(myapi.locations, ['/tmp/tvshows'])

        with mock.patch.object(api.service, 'prepare_service'):
            self.CONF.set_override(
                'locations',
                ['/tmp/download/shows'])

            myapi = api.API()
            myapi.add_locations(['/tmp/tvshows'])
            self.assertEqual(myapi.locations, ['/tmp/download/shows',
                                               '/tmp/tvshows'])

    def test_get_results(self):
        good_ep = mock.Mock(spec=episode.Episode)
        good_ep.original = '/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4'
        good_ep.formatted_filename = 'S04E12-Madness.mp4'

        bad_ep = mock.Mock(spec=episode.Episode)
        bad_ep.original = '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv'
        bad_ep.formatted_filename = None
        bad_ep.messages = ['Could not find season 20']

        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            myapi.episodes = [good_ep]
            myapi.failed_episodes = [bad_ep]
            self.assertEqual(
                myapi.get_results(),
                {'/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4': {
                    'formatted_filename': 'S04E12-Madness.mp4',
                    'result': True,
                    'messages': None,
                    },
                 '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv': {
                     'formatted_filename': None,
                     'result': False,
                     'messages': 'Could not find season 20',
                     }})

    @mock.patch.object(services, 'get_service',
                       return_value=mock.Mock(spec=services.base.Service))
    def test_find_files(self, mock_service):

        orig_files = ['/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4',
                      '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv']
        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()

            with mock.patch.object(api.tools, 'retrieve_files',
                                   return_value=orig_files):
                self.assertTrue(myapi.find_files())

    def test_valid_files(self):
        good_ep = episode.Episode(
            '/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4')
        good_ep._valid = True
        good_ep.formatted_filename = 'S04E12-Madness.mp4'

        bad_ep = episode.Episode(
            '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv')
        bad_ep._valid = False
        bad_ep.formatted_filename = None
        bad_ep.messages = ['Could not find season 20']

        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            myapi.episodes = [good_ep, bad_ep]
            self.assertTrue(myapi.valid_files())
            self.assertEqual(len(myapi.episodes), 1)
            self.assertEqual(len(myapi.failed_episodes), 1)

    @mock.patch.object(os, 'access', return_value=True)
    def test_parse_files(self, mock_access):
        good_ep = episode.Episode(
            '/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4')

        bad_ep = episode.Episode(
            '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv')

        fail_ep = episode.Episode(
            '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv')
        fail_ep._valid = False

        strerr_ep = episode.Episode(
            '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv')
        strerr_ep._valid = True

        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            myapi.episodes = [good_ep, bad_ep, fail_ep, strerr_ep]
            self.assertTrue(myapi.parse_files())
            self.assertEqual(len(myapi.episodes), 2)
            self.assertEqual(len(myapi.failed_episodes), 2)

    def test_enhance_files(self):
        good_ep = episode.Episode(
            '/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4')
        good_ep._valid = True
        good_ep.series_name = 'revenge'
        good_ep.episode_numbers = [12]
        good_ep.season_number = 4

        bad_ep = episode.Episode(
            '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv')
        bad_ep._valid = True
        bad_ep.series_name = 'Lucy'
        bad_ep.episode_numbers = [14]
        bad_ep.season_number = 20

        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            myapi.episodes = [good_ep, bad_ep]
            self.assertTrue(myapi.enhance_files())
            self.assertEqual(len(myapi.episodes), 1)
            self.assertEqual(len(myapi.failed_episodes), 1)

            with mock.patch.object(services.tvdb.TvdbService,
                                   'get_episode_name',
                                   side_effect=AttributeError):
                self.assertFalse(myapi.enhance_files())

    def test_rename_files(self):
        good_ep = episode.Episode(
            '/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4')
        good_ep._valid = True
        good_ep.series_name = 'revenge'
        good_ep.episode_numbers = [12]
        good_ep.season_number = 4

        bad_ep = episode.Episode(
            '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv')
        bad_ep._valid = True
        bad_ep.series_name = 'Lucy'
        bad_ep.episode_numbers = [14]
        bad_ep.season_number = 20

        with mock.patch.object(api.service, 'prepare_service'):
            myapi = api.API()
            myapi.episodes = [good_ep, bad_ep]
            with mock.patch.object(good_ep, 'execute_rename'):
                with mock.patch.object(bad_ep, 'execute_rename',
                                       side_effect=OSError):
                    self.assertTrue(myapi.rename_files())

    def test_execute(self):

        with mock.patch.object(api.service, 'prepare_service'):
            with mock.patch.object(api.API, 'find_files', return_value=False):
                self.assertIsInstance(api.API.execute(), dict)
            with mock.patch.object(api.API, 'find_files', return_value=True):
                with mock.patch.object(api.API, 'valid_files',
                                       return_value=False):
                    self.assertIsInstance(api.API.execute(), dict)
                with mock.patch.object(api.API, 'valid_files',
                                       return_value=True):
                    with mock.patch.object(api.API, 'parse_files',
                                           return_value=False):
                        self.assertIsInstance(api.API.execute(), dict)
                    with mock.patch.object(api.API, 'parse_files',
                                           return_value=True):
                        with mock.patch.object(api.API, 'enhance_files',
                                               return_value=False):
                            self.assertIsInstance(api.API.execute(), dict)
                        with mock.patch.object(api.API, 'enhance_files',
                                               return_value=True):
                            with mock.patch.object(api.API, 'rename_files',
                                                   return_value=False):
                                self.assertIsInstance(api.API.execute(), dict)
                            with mock.patch.object(api.API, 'rename_files',
                                                   return_value=True):
                                self.assertIsInstance(api.API.execute(), dict)
