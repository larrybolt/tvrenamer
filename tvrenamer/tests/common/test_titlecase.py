from oslotest import base as test_base

from tvrenamer.common import titlecase


class TitlecaseTest(test_base.BaseTestCase):

    def test_from_all_lower(self):
        self.assertEqual(titlecase('a very simple title'),
                         'A Very Simple Title')
        self.assertEqual(titlecase('o\'shea is not a good band'),
                         'O\'Shea Is Not a Good Band')
        self.assertEqual(titlecase('o\'do not wanton with those eyes'),
                         'O\'DO Not Wanton With Those Eyes')

    def test_from_all_upper(self):
        self.assertEqual(titlecase('A VERY SIMPLE TITLE'),
                         'A Very Simple Title')
        self.assertEqual(titlecase('W.KI.N.YR.'), 'W.KI.N.YR.')

    def test_from_notation(self):
        self.assertEqual(titlecase('funtime.example.com'),
                         'funtime.example.com')

        self.assertEqual(titlecase('Funtime.Example.Com'),
                         'Funtime.Example.Com')

    def test_from_location(self):
        self.assertEqual(
            titlecase('sample series/season 9/s09e01 - sample episode'),
            'Sample Series/Season 9/S09e01 - Sample Episode')

    def test_from_mac(self):
        self.assertEqual(titlecase('macyhg'), 'MacYhg')

    def test_from_asis(self):
        self.assertEqual(titlecase('A Very Simple Title'),
                         'A Very Simple Title')
