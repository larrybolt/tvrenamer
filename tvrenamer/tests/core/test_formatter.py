import mock
import six

from tvrenamer.core import formatter
from tvrenamer.tests import base


class FormatterTest(base.BaseTest):

    def test_replace_series_name(self):
        self.CONF.set_override('input_series_replacements', dict())
        name = 'Reign'
        self.assertEqual(
            formatter._replace_series_name(
                name, self.CONF.input_series_replacements),
            'Reign')

        self.CONF.set_override('input_series_replacements',
                               {'reign (2013)': 'reign'})
        name = 'Reign'
        self.assertEqual(
            formatter._replace_series_name(
                name, self.CONF.input_series_replacements),
            'Reign')

        self.CONF.set_override('input_series_replacements',
                               {'reign': 'reign (2013)'})
        name = 'Reign'
        self.assertEqual(
            formatter._replace_series_name(
                name, self.CONF.input_series_replacements),
            'reign (2013)')

    def test_clean_series_name(self):
        self.CONF.set_override('input_series_replacements', dict())

        self.assertIsNone(formatter.clean_series_name(None))
        self.assertEqual(formatter.clean_series_name(''), '')

        name = 'an.example.1.0.test'
        self.assertEqual(formatter.clean_series_name(name),
                         'an example 1.0 test')

        name = 'an_example_1.0_test'
        self.assertEqual(formatter.clean_series_name(name),
                         'an example 1.0 test')

    def test_apply_replacements(self):
        self.assertEqual('sample.avi',
                         formatter.apply_replacements('sample.avi', None))
        self.assertEqual('sample.avi',
                         formatter.apply_replacements('sample.avi', []))

        reps = [{'match': '_test',
                 'replacement': '',
                 'with_extension': False,
                 'is_regex': False},
                ]
        self.assertEqual('sample.avi',
                         formatter.apply_replacements('sample_test.avi', reps))

        reps = [{'match': '_test',
                 'replacement': '',
                 'with_extension': True,
                 'is_regex': False},
                ]
        self.assertEqual('sample.avi',
                         formatter.apply_replacements('sample_test.avi', reps))

        reps = [{'match': '[ua]+',
                 'replacement': 'x',
                 'with_extension': False,
                 'is_regex': True},
                ]
        self.assertEqual('sxmple_test.avi',
                         formatter.apply_replacements('sample_test.avi', reps))

    def test_format_episode_numbers(self):
        epnums = [1]
        self.assertEqual(formatter._format_episode_numbers(epnums),
                         '01')

        epnums = [1, 2, 3, 4, 5]
        self.assertEqual(formatter._format_episode_numbers(epnums),
                         '01-02-03-04-05')

    def test_format_episode_name(self):
        names = ['Pilot']
        self.assertEqual(formatter._format_episode_name(names),
                         'Pilot')

        names = ['Pilot (1)', 'Pilot (2)']
        self.assertEqual(formatter._format_episode_name(names),
                         'Pilot (1-2)')

        names = ['From Hell', 'And Back']
        self.assertEqual(formatter._format_episode_name(names),
                         'From Hell, And Back')

    def test_make_valid_filename(self):
        # normal - asis
        name = 'person.of.interest.s04e10.proper.hdtv.x264-w4f.mp4'
        self.assertEqual(formatter._make_valid_filename(name),
                         'person.of.interest.s04e10.proper.hdtv.x264-w4f.mp4')

        name = '.sample.filename'
        self.assertEqual(formatter._make_valid_filename(name),
                         '_.sample.filename')

        name = six.u('foo\xf1bar')
        self.assertEqual(formatter._make_valid_filename(name),
                         'foobar')

        with mock.patch.object(formatter.platform, 'system',
                               return_value='FreeBSD'):
            # / (all OS)
            name = 'person.of.interest.s04/e10.x264/-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest.s04_e10.x264_-w4f.mp4')

        with mock.patch.object(formatter.platform, 'system',
                               return_value='Linux'):
            # / (all OS)
            name = 'person.of.interest.s04/e10.x264/-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest.s04_e10.x264_-w4f.mp4')

        with mock.patch.object(formatter.platform, 'system',
                               return_value='Darwin'):
            # / (all OS)
            name = 'person.of.interest.s04/e10.x264/-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest.s04_e10.x264_-w4f.mp4')

            # :
            name = 'person.of.interest:.s04e10:.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

        with mock.patch.object(formatter.platform, 'system',
                               return_value='Java'):
            # / (all OS)
            name = 'person.of.interest.s04/e10.x264/-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest.s04_e10.x264_-w4f.mp4')

            # :
            name = 'person.of.interest:.s04e10:.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # *
            name = 'person.of.interest*.s04e10*.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # ?
            name = 'person.of.interest?.s04e10?.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # "
            name = 'person.of.interest".s04e10".x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # <
            name = 'person.of.interest<.s04e10<.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # >
            name = 'person.of.interest>.s04e10>.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # |
            name = 'person.of.interest|.s04e10|.x264-w4f.mp4'
            self.assertEqual(formatter._make_valid_filename(name),
                             'person.of.interest_.s04e10_.x264-w4f.mp4')

            # major naming issues
            name = '\\/:*?<Evil>|\"'
            self.assertEqual(formatter._make_valid_filename(name),
                             '______Evil___')

            name = 'CON.avi'
            self.assertEqual(formatter._make_valid_filename(name),
                             '_CON.avi')

        name = 'MJR1uc9JlkfFrnBjFlUQCpICUc6wl93wie4PmbjYbwj7j4j9MMrsWNG0yOJiheAwZkpRMgP1KBICoFN3ZztkciqZlmaXUeToJuh6hT9cTHXqoghCbRVUNxP6JzIqrXB.OHcpQb0vojDr5fIMPu3Fgjzh9kaG3WYE9zHUmC8co2FjNBUiBIKHAMB73HBXpF4Y54eCg0CXTB29hhkDwbRsvWYn0i9tPE6kTsgVyQNb36S71aDqvuMmZp0ll3YIsrZXX'  # noqa
        self.assertEqual(formatter._make_valid_filename(name),
                         'MJR1uc9JlkfFrnBjFlUQCpICUc6wl93wie4PmbjYbwj7j4j9MMrsWNG0yOJiheAwZkpRMgP1KBICoFN3ZztkciqZlmaXUeToJuh6hT9cTHXqoghCbRVUNxP6JzIqrXB.OHcpQb0vojDr5fIMPu3Fgjzh9kaG3WYE9zHUmC8co2FjNBUiBIKHAMB73HBXpF4Y54eCg0CXTB29hhkDwbRsvWYn0i9tPE6kTsgVyQNb36S71aDqvuMmZp0ll3YIsr')  # noqa

        name = 'ykgoibnaioyabclikamnxbikiaujdjkvlhywrnhtyzbylugtcaxomlrbtpnqgvscrhqvkydnohwvhiusnkrjyrueqnjcpvwzuhpitmrtwwzmptkaxzgwzzjdgwlwswozniwilazcbrokqnlqdjnwoykuiejjvizpoiitcoiqvzuvcuwmcfsw.jfvxeujzshxjhcllrsemormrfknzfsoczbuisqmexamsrzifuoxjxysicikfgegjwkojyrokijxyefekyilqsnwaqkgiyuayasac'  # noqa
        self.assertEqual(formatter._make_valid_filename(name),
                         'ykgoibnaioyabclikamnxbikiaujdjkvlhywrnhtyzbylugtcaxomlrbtpnqgvscrhqvkydnohwvhiusnkrjyrueqnjcpvwzuhpitmrtwwzmptkaxzgwzzjdgwlwswozniwilazcbrokqnlqdjnwoykui.jfvxeujzshxjhcllrsemormrfknzfsoczbuisqmexamsrzifuoxjxysicikfgegjwkojyrokijxyefekyilqsnwaqkgiyuayasac')  # noqa

    def test_format_filename(self):
        self.CONF.set_override(
            'filename_format_ep',
            'S%(seasonnumber)02dE%(episode)s-%(episodename)s%(ext)s')
        self.CONF.set_override('output_filename_replacements',
                               [])
        self.assertEqual(formatter.format_filename(None, 2, [2],
                                                   ['The Codpiece Topology'],
                                                   '.avi'),
                         'S02E02-The Codpiece Topology.avi')

        self.CONF.set_override(
            'filename_format_ep',
            '%(seriesname)s - S%(seasonnumber)02dE%(episode)s-%(episodename)s%(ext)s')  # noqa
        self.assertEqual(formatter.format_filename('the big bang theory',
                                                   2, [2],
                                                   ['The Codpiece Topology'],
                                                   '.avi'),
                         'The Big Bang Theory - S02E02-The Codpiece Topology.avi')  # noqa

        self.CONF.set_override(
            'filename_format_ep',
            '%(seriesname)s - S%(seasonnumber)02dE%(episode)s-%(episodename)s%(ext)s')  # noqa
        self.CONF.set_override('output_filename_replacements',
                               [{'match': 'Heartland (2007) (CA)',
                                 'replacement': 'Heartland (CA)'}])
        self.assertEqual(formatter.format_filename('Heartland (2007) (CA)',
                                                   2, [2],
                                                   ['Letting Go'],
                                                   '.mp4'),
                         'Heartland (CA) - S02E02-Letting Go.mp4')

    def test_format_dirname(self):
        self.CONF.set_override(
            'directory_name_format',
            '%(seriesname)s/Season %(seasonnumber)02d')
        self.assertEqual(formatter.format_dirname('Sample Series', 2),
                         'Sample Series/Season 02')

    @mock.patch('os.path.isdir')
    def test_find_library(self, mock_isdir):
        series_path = 'The Big Bang Theory/Season 01'
        locations = ['\\NAS/Share/Video/Current',
                     '\\NAS/Share/Video/Offair',
                     '/local/video']
        default_location = '\\NAS/Share/Video/TBD'

        self.CONF.set_override('libraries', locations)
        self.CONF.set_override('default_library', default_location)

        mock_isdir.return_value = True
        result = formatter.find_library(series_path)
        self.assertEqual(result, '\\NAS/Share/Video/Current')

        mock_isdir.return_value = False
        result = formatter.find_library(series_path)
        self.assertEqual(result, default_location)

        mock_isdir.side_effect = (False, False, False, False, False, True)
        result = formatter.find_library(series_path)
        self.assertEqual(result, '/local/video')
