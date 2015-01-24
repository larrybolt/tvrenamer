import os

import mock

from tvrenamer.core import episode
from tvrenamer import exceptions as exc
from tvrenamer.tests import base


class EpisodeTest(base.BaseTest):

    def setUp(self):
        super(EpisodeTest, self).setUp()

        self.media = self.create_tempfiles(
            [('revenge.s04e12.hdtv.x264-2hd', 'dummy data')],
            '.mp4')[0]
        self.filename = os.path.basename(self.media)
        self.dirname = os.path.dirname(self.media)

    def test_str_repr(self):
        ep = episode.Episode(self.media)
        ep_str = '<Episode>:'
        ep_str += self.media
        ep_str += ' => ['
        ep_str += self.dirname
        ep_str += ' '
        ep_str += self.filename
        ep_str += '|None .mp4] '
        ep_str += 'meta: ['
        ep_str += ' S E[]] '
        ep_str += 'formatted: /'
        self.assertEqual(str(ep), ep_str)
        self.assertEqual(repr(ep), ep_str)

    def test_call(self):
        ep = episode.Episode(self.media)
        with mock.patch.object(ep, 'parse'):
            with mock.patch.object(ep, 'enhance'):
                with mock.patch.object(ep, 'rename'):
                    ep()
                    self.assertEqual(ep.state, episode.const.DONE)

        ep = episode.Episode(self.media)
        with mock.patch.object(ep, 'parse', side_effect=OSError):
            ep()
            self.assertEqual(ep.state, episode.const.FAILED)

        ep = episode.Episode(self.media)
        with mock.patch.object(ep, 'parse',
                               side_effect=exc.NoValidFilesFoundError):
            ep()
            self.assertEqual(ep.state, episode.const.FAILED)

    def test_status(self):
        ep = episode.Episode(self.media)
        self.assertTrue(self.media in ep.status)

    def test_validate(self):
        ep = episode.Episode(self.media)
        self.assertTrue(ep.valid)

        ep = episode.Episode(self.media)
        with mock.patch.object(os, 'access', return_value=False):
            self.assertFalse(ep.valid)

        ep = episode.Episode(self.media)
        with mock.patch.object(episode.tools, 'is_valid_extension',
                               return_value=False):
            self.assertFalse(ep.valid)

        ep = episode.Episode(self.media)
        with mock.patch.object(episode.tools, 'is_blacklisted_filename',
                               return_value=True):
            self.assertFalse(ep.valid)

    def test_parse(self):
        ep = episode.Episode(self.media)
        ep.parse()
        self.assertEqual(ep.episode_numbers, [12])
        self.assertEqual(ep.series_name, 'revenge')
        self.assertEqual(ep.season_number, 4)

        ep = episode.Episode(self.media)
        ep._valid = False
        self.assertRaises(exc.NoValidFilesFoundError, ep.parse)

        ep = episode.Episode(self.media)
        with mock.patch.object(episode.parser, 'parse_filename',
                               return_value=None):
            self.assertRaises(exc.InvalidFilename, ep.parse)

        ep = episode.Episode(self.media)
        with mock.patch.object(episode.parser, 'parse_filename',
                               return_value={'pattern': ''}):
            self.assertRaises(exc.ConfigValueError, ep.parse)

        ep = episode.Episode(self.media)
        with mock.patch.object(episode.parser, 'parse_filename',
                               return_value={'pattern': '',
                                             'episode_numbers': []}):
            self.assertRaises(exc.ConfigValueError, ep.parse)

    def test_enhance(self):
        ep = episode.Episode(self.media)
        ep.parse()
        with mock.patch.object(ep.api, 'get_series_by_name',
                               return_value=(None, '')):
            self.assertRaises(exc.ShowNotFound, ep.enhance)

        with mock.patch.object(ep.api, 'get_series_by_name',
                               return_value=({}, '')):
            with mock.patch.object(ep.api, 'get_series_name',
                                   return_value='Revenge'):
                with mock.patch.object(ep.api, 'get_episode_name',
                                       return_value=(['Madness'], None)):
                    ep.enhance()
                    self.assertEqual(ep.series_name, 'Revenge')
                    self.assertEqual(ep.episode_names, ['Madness'])

        ep = episode.Episode(self.media)
        ep.parse()
        with mock.patch.object(ep.api, 'get_series_by_name',
                               return_value=({}, '')):
            with mock.patch.object(ep.api, 'get_series_name',
                                   return_value='Revenge'):
                with mock.patch.object(ep.api, 'get_episode_name',
                                       return_value=(None, '')):
                    self.assertRaises(exc.EpisodeNotFound, ep.enhance)

    def test_gen_filename(self):
        ep = episode.Episode(self.media)
        ep.series_name = 'Revenge'
        ep.season_number = 4
        ep.episode_numbers = [12]
        ep.episode_names = ['Madness']
        self.assertEqual(ep._format_filename(),
                         'Revenge - 04x12 - Madness.mp4')
        self.CONF.set_override(
            'filename_format_ep',
            'S%(seasonnumber)02dE%(episode)s-%(episodename)s%(ext)s')
        self.assertEqual(ep._format_filename(), 'S04E12-Madness.mp4')

    def test_gen_dirname(self):
        ep = episode.Episode(self.media)
        ep.series_name = 'Revenge'
        ep.season_number = 4
        self.assertEqual(ep._format_dirname(), '.')
        self.CONF.set_override('directory_name_format',
                               '%(seriesname)s/Season %(seasonnumber)02d')
        self.assertEqual(ep._format_dirname(), 'Revenge/Season 04')

    def test_rename(self):
        ep = episode.Episode(self.media)
        ep.series_name = 'Revenge'
        ep.season_number = 4
        ep.episode_numbers = [12]
        ep.episode_names = ['Madness']

        self.CONF.set_override('move_files_enabled', False)
        with mock.patch.object(episode.renamer, 'execute') as mock_renamer:
            ep.rename()
            mock_renamer.assert_called_with(
                self.media,
                os.path.join(self.dirname, 'Revenge - 04x12 - Madness.mp4'))

        self.CONF.set_override('move_files_enabled', True)
        with mock.patch.object(episode.renamer, 'execute') as mock_renamer:
            with mock.patch.object(episode.tools, 'find_library',
                                   return_value='/tmp'):
                ep.rename()
                mock_renamer.assert_called_with(
                    self.media,
                    os.path.join('/tmp', '.', 'Revenge - 04x12 - Madness.mp4'))
