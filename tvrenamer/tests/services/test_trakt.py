import os

import testtools

from tvrenamer.services import trakt_service
from tvrenamer.tests import base


def disabled():
    return not os.environ.get('TEST_TRAKT_CLIENT_ID') or not os.environ.get(
        'TEST_TRAKT_CLIENT_SECRET')


class TraktServiceTest(base.BaseTest):

    def setUp(self):
        super(TraktServiceTest, self).setUp()

        self.CONF.set_override('client_id',
                               os.environ.get('TEST_TRAKT_CLIENT_ID'),
                               'trakt')
        self.CONF.set_override('client_secret',
                               os.environ.get('TEST_TRAKT_CLIENT_SECRET'),
                               'trakt')
        self.api = trakt_service.TraktService()

    def test_list_opts(self):
        self.assertIsNotNone(trakt_service.list_opts())

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_series_by_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series.title, 'The Big Bang Theory')

        series, err = self.api.get_series_by_name('Fake - Unknown Series')
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertEqual(err, 'Not Found')

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_series_by_id(self):
        series, err = self.api.get_series_by_id(1409)
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series.title, 'The Big Bang Theory')

        series, err = self.api.get_series_by_id(0)
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertEqual(err, 'Not Found')

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_series_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(
            self.api.get_series_name(series),
            'The Big Bang Theory')

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        episodes, eperr = self.api.get_episode_name(series, [1], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Pilot'])

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name_season_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 2)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertEqual(eperr,
                         'Not Found - "method exists, but no record found"')

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name_attr_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 5)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertEqual(eperr,
                         'Not Found - "method exists, but no record found"')

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name_episode_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [25], 1)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertEqual(eperr,
                         'Not Found - "method exists, but no record found"')

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 0)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Serenity'])
