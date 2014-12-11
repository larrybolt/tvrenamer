import os

import mock

from tvrenamer.common import tools
from tvrenamer.tests import base


class ToolsTest(base.BaseTest):

    def test_make_opt_list(self):
        group_name = 'test'
        options = ['x', 'y', 'z', 'v']
        results = tools.make_opt_list(options, group_name)
        self.assertEqual(results, [('test', ['x', 'y', 'z', 'v'])])

    def test_split_extension(self):
        pass

    def test_apply_replacements(self):
        pass

    def test_is_valid_extension(self):
        valids = ['.avi', '.mp4', '.mkv', 'mpg']
        self.assertTrue(tools.is_valid_extension('.avi', valids))
        self.assertTrue(tools.is_valid_extension('.mp4', valids))
        self.assertTrue(tools.is_valid_extension('.mkv', valids))
        self.assertTrue(tools.is_valid_extension('.mpg', valids))

        self.assertFalse(tools.is_valid_extension('.mov', valids))
        self.assertFalse(tools.is_valid_extension('', valids))
        self.assertFalse(tools.is_valid_extension(None, valids))

        self.assertTrue(tools.is_valid_extension('.mov', []))
        self.assertTrue(tools.is_valid_extension('.mov', None))

    def test_is_blacklisted_filename(self):
        pass

    def test_retrieve_files(self):
        with mock.patch.object(os, 'walk',
                               return_value=[('/tmp/videos',
                                             [],
                                             ['video1.mp4',
                                              'video2.avi',
                                              'video3.mkv',
                                              'video4.mov'])]):
            files = tools.retrieve_files(['/tmp/videos'])
            self.assertEqual(files, ['/tmp/videos/video1.mp4',
                                     '/tmp/videos/video2.avi',
                                     '/tmp/videos/video3.mkv',
                                     '/tmp/videos/video4.mov'])

        with mock.patch.object(os, 'walk',
                               return_value=[('\\NAS/Share/Video',
                                              [],
                                              ['video1.mp4',
                                               'video2.avi',
                                               'video3.mkv',
                                               'video4.mov'])]):
            files = tools.retrieve_files(['\\NAS/Share/Video'])
            self.assertEqual(files, ['\\NAS/Share/Video/video1.mp4',
                                     '\\NAS/Share/Video/video2.avi',
                                     '\\NAS/Share/Video/video3.mkv',
                                     '\\NAS/Share/Video/video4.mov'])

    def test_find_library(self):
        series_path = 'The Big Bang Theory/Season 01'
        locations = ['\\NAS/Share/Video/Current',
                     '\\NAS/Share/Video/Offair',
                     '/local/video']
        default_location = '\\NAS/Share/Video/TBD'

        with mock.patch.object(os.path, 'isdir', return_value=True):
            result = tools.find_library(series_path,
                                        locations,
                                        default_location)
            self.assertEqual(result, '\\NAS/Share/Video/Current')

        with mock.patch.object(os.path, 'isdir', return_value=False):
            result = tools.find_library(series_path,
                                        locations,
                                        default_location)
            self.assertEqual(result, default_location)

        return_values = (False, False, False, False, False, True)
        with mock.patch.object(os.path, 'isdir', side_effect=return_values):
            result = tools.find_library(series_path,
                                        locations,
                                        default_location)
            self.assertEqual(result, '/local/video')
