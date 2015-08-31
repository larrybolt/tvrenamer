from tvrenamer.core import parser
from tvrenamer.tests import base


class ParserTest(base.BaseTest):

    def test_parse_filename(self):
        fname = 'Sample-Show.S02E15'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [15])

        fname = 'Sample-Show'
        result = parser.parse_filename(fname)
        self.assertIsNone(result)

        fname = 'Sample-Show.S02E15'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [15])

        fname = 'The Wire s05e10 30.mp4'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'The Wire', result)
        self.assertEqual(result['season_number'], 5)
        self.assertEqual(result['episode_numbers'], [10])

        fname = '30 Rock [2.10] Episode 210.avi'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], '30 Rock', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [10])

    def test_parse_expr1(self):
        fname = 'Sample.Show.S01E01.S01E02.S01E03.S01E04.eps.mp4'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [1, 2, 3, 4])

    def test_parse_expr2(self):
        fname = 'Sample-Show.S02e22e23e24'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [22, 23, 24])

    def test_parse_expr3(self):
        fname = 'Sample.Show.3x12.3x13.3x14'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 3)
        self.assertEqual(result['episode_numbers'], [12, 13, 14])

    def test_parse_expr4(self):
        fname = 'Sample.Show.4x4x5x6'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 4)
        self.assertEqual(result['episode_numbers'], [4, 5, 6])

    def test_parse_expr5(self):
        fname = 'Sample.Show.S02E11-15-'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [11, 12, 13, 14, 15])

    def test_parse_expr6(self):
        fname = 'Sample-Show.2x11-15'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [11, 12, 13, 14, 15])

        fname = 'Sample-Show.2x15-12'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [12, 13, 14, 15])

    def test_parse_expr7(self):
        fname = 'Sample-Show.[3x11-13]'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 3)
        self.assertEqual(result['episode_numbers'], [11, 12, 13])

    def test_parse_expr8(self):
        fname = 'Sample.Show-[013]'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [13])

    def test_parse_expr9(self):
        fname = 'Sample.S0202'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample', result)
        self.assertEqual(result['season_number'], 2)
        self.assertEqual(result['episode_numbers'], [2])

    def test_parse_expr10(self):
        fname = 'Sample_Show-7x17'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample_Show', result)
        self.assertEqual(result['season_number'], 7)
        self.assertEqual(result['episode_numbers'], [17])

    def test_parse_expr11(self):
        fname = 'Sample-Show S09.E11'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 9)
        self.assertEqual(result['episode_numbers'], [11])

        fname = 'Sample-Show S09_E11'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 9)
        self.assertEqual(result['episode_numbers'], [11])

        fname = 'Sample-Show S09 - E11'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample-Show', result)
        self.assertEqual(result['season_number'], 9)
        self.assertEqual(result['episode_numbers'], [11])

    def test_parse_expr12(self):
        fname = 'Sample_Show-[09.01]'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample_Show', result)
        self.assertEqual(result['season_number'], 9)
        self.assertEqual(result['episode_numbers'], [1])

    def test_parse_expr13(self):
        fname = 'Sample.Show - S9 E 9'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 9)
        self.assertEqual(result['episode_numbers'], [9])

    def test_parse_expr14(self):
        fname = 'SampleShow - episode 1219 [S 13 - E 07]'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'SampleShow', result)
        self.assertEqual(result['season_number'], 13)
        self.assertEqual(result['episode_numbers'], [7])

        fname = 'SampleShow - episode 1219 [S 13 Ep 07]'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'SampleShow', result)
        self.assertEqual(result['season_number'], 13)
        self.assertEqual(result['episode_numbers'], [7])

    def test_parse_expr15(self):
        fname = 'Sample Show 2 of 7'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [2])

    def test_parse_expr16(self):
        fname = 'Sample.Show.Part.1.and.Part.2 '
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [1, 2])

        fname = 'Sample.Show.pt.1 & pt 2 & pt.3 '
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [1, 2, 3])

    def test_parse_expr17(self):
        fname = 'Sample Show part 5 '
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [5])

    def test_parse_expr18(self):
        fname = 'Sample.Show season 10 episode 15'
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample.Show', result)
        self.assertEqual(result['season_number'], 10)
        self.assertEqual(result['episode_numbers'], [15])

    def test_parse_expr19(self):
        fname = 'Sample Show 909 '
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample Show', result)
        self.assertEqual(result['season_number'], 9)
        self.assertEqual(result['episode_numbers'], [9])

    def test_parse_expr20(self):
        fname = 'Sample Show 1011 '
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample Show', result)
        self.assertEqual(result['season_number'], 10)
        self.assertEqual(result['episode_numbers'], [11])

    def test_parse_expr21(self):
        fname = 'Sample Show e19 '
        result = parser.parse_filename(fname)
        self.assertEqual(result['series_name'], 'Sample Show', result)
        self.assertEqual(result['season_number'], 1)
        self.assertEqual(result['episode_numbers'], [19])
