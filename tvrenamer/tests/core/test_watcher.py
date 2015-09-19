import mock

from tvrenamer.core import watcher
from tvrenamer.tests import base


class WatcherTests(base.BaseTest):

    def test_is_valid_extension(self):

        valids = ['.avi', '.mp4', '.mkv', 'mpg']
        self.CONF.set_override('valid_extensions', valids)

        self.assertTrue(watcher._is_valid_extension('.avi'))
        self.assertTrue(watcher._is_valid_extension('.mp4'))
        self.assertTrue(watcher._is_valid_extension('.mkv'))
        self.assertTrue(watcher._is_valid_extension('.mpg'))

        self.assertFalse(watcher._is_valid_extension('.mov'))
        self.assertFalse(watcher._is_valid_extension(''))
        self.assertFalse(watcher._is_valid_extension(None))

        self.CONF.set_override('valid_extensions', [])
        self.assertTrue(watcher._is_valid_extension('.mov'))

        self.CONF.set_override('valid_extensions', None)
        self.assertTrue(watcher._is_valid_extension('.mov'))

    def test_is_blacklisted_filename(self):

        self.CONF.set_override('filename_blacklist', None)
        self.assertFalse(watcher._is_blacklisted_filename(None))

        blacklist = ['readme.txt', '.DS_File']
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertFalse(watcher._is_blacklisted_filename('/tmp/test.avi'))
        self.assertTrue(watcher._is_blacklisted_filename('/tmp/.DS_File'))

        blacklist = [{'full_path': '',
                      'exclude_extension': False,
                      'is_regex': False,
                      'match': '.DS_File'}]
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertTrue(watcher._is_blacklisted_filename('/tmp/.DS_File'))

        blacklist = [{'full_path': '',
                      'exclude_extension': True,
                      'is_regex': False,
                      'match': '.DS_File'}]
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertTrue(watcher._is_blacklisted_filename('/tmp/.DS_File'))

        blacklist = [{'full_path': '',
                      'exclude_extension': True,
                      'is_regex': False,
                      'match': '.DS_File'}]
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertFalse(watcher._is_blacklisted_filename('/tmp/sample.avi'))

        blacklist = [{'full_path': True,
                      'exclude_extension': True,
                      'is_regex': False,
                      'match': '.DS_File'}]
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertFalse(watcher._is_blacklisted_filename('/tmp/sample.avi'))

        blacklist = [{'full_path': '',
                      'exclude_extension': True,
                      'is_regex': True,
                      'match': '.*fake.*'}]
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertTrue(watcher._is_blacklisted_filename('/tmp/test_fake.avi'))

        blacklist = [{'full_path': '',
                      'exclude_extension': True,
                      'is_regex': True,
                      'match': '.*fake.*'}]
        self.CONF.set_override('filename_blacklist', blacklist)
        self.assertFalse(watcher._is_blacklisted_filename('/tmp/sample.avi'))

    @mock.patch('os.access')
    @mock.patch('os.walk')
    def test_retrieve_files(self, mock_walk, mock_access):
        mock_access.return_value = True
        mock_walk.return_value = [('/tmp/videos', [],
                                   ['video1.mp4',
                                    'video2.avi',
                                    'video3.mkv',
                                    'video4.mov']
                                   )]

        locations = ['/tmp/videos']
        self.CONF.set_override('locations', locations)
        self.assertEqual(watcher.retrieve_files(),
                         ['/tmp/videos/video1.mp4',
                          '/tmp/videos/video2.avi',
                          '/tmp/videos/video3.mkv',
                          '/tmp/videos/video4.mov'])

    @mock.patch('os.access')
    @mock.patch('os.walk')
    def test_retrieve_files_no_results(self, mock_walk, mock_access):
        mock_access.return_value = False
        mock_walk.return_value = [('/tmp/videos', [],
                                   ['video1.mp4']
                                   )]

        locations = ['/tmp/videos']
        self.CONF.set_override('locations', locations)
        self.assertEqual(watcher.retrieve_files(), [])

    @mock.patch('os.access')
    @mock.patch('os.walk')
    def test_retrieve_files_nas_path(self, mock_walk, mock_access):
        mock_access.return_value = True
        mock_walk.return_value = [('\\NAS/Share/Video', [],
                                   ['video1.mp4',
                                    'video2.avi',
                                    'video3.mkv',
                                    'video4.mov']
                                   )]

        locations = ['\\NAS/Share/Video']
        self.CONF.set_override('locations', locations)
        self.assertEqual(watcher.retrieve_files(),
                         ['\\NAS/Share/Video/video1.mp4',
                          '\\NAS/Share/Video/video2.avi',
                          '\\NAS/Share/Video/video3.mkv',
                          '\\NAS/Share/Video/video4.mov'])
