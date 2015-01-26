from __future__ import print_function

import testtools
import tvrage_api

from tvrenamer.services import tvrage
from tvrenamer.tests import base


def is_unavailable():
    try:
        tvrage_api.search_show(sid='2930')
        print('search successful')
    except tvrage_api.TvrageServiceUnavailable:
        # if connection or timeout happens then consider
        # the service unavailable and we will skip tests
        print('service unavailable')
        return True
    except Exception as err:
        print('other exception;', type(err), str(err))
        pass
    # any other issues then we need to continue with testing
    return False


SERVICE_UNAVAILABLE = is_unavailable()


class TvrageServiceTest(base.BaseTest):

    def setUp(self):
        super(TvrageServiceTest, self).setUp()
        self.api = tvrage.TvrageService()

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_series_by_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesname'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_name('Fake - Unknown Series')
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, tvrage_api.TvrageShowNotFound)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_series_by_id(self):
        series, err = self.api.get_series_by_id(8511)
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesname'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_id(0)
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, tvrage_api.TvrageShowNotFound)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_series_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(self.api.get_series_name(series),
                         'The Big Bang Theory')

        self.assertIsNone(self.api.get_series_name(None))

        self.CONF.set_override('output_series_replacements',
                               {'reign (2013)': 'reign'})
        series, err = self.api.get_series_by_name('reign (2013)')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(self.api.get_series_name(series), 'reign')

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_episode_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        episodes, eperr = self.api.get_episode_name(series, [1], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Pilot'])

        episodes, eperr = self.api.get_episode_name(None, [1], 1)
        self.assertIsNone(episodes)
        self.assertIsNone(eperr)

        episodes, eperr = self.api.get_episode_name(series, [1])
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Pilot'])

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_episode_name_season_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 2)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvrage_api.TvrageSeasonNotFound)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], '1')
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvrage_api.TvrageSeasonNotFound)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_episode_name_attr_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 'xx')
        self.assertIsNone(episodes)
        self.assertIsNone(eperr)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVRage service unavailable')
    def test_get_episode_name_episode_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [25], 1)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvrage_api.TvrageEpisodeNotFound)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [15], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Serenity'])
