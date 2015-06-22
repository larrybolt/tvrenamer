from __future__ import print_function

import testtools
import tvdb_api

from tvrenamer.services import tvdb
from tvrenamer.tests import base


def is_unavailable():
    try:
        api = tvdb_api.Tvdb()
        api[80379]
        print('search successful')
    except tvdb_api.tvdb_error as dberr:
        # if connection or timeout happens then consider
        # the service unavailable and we will skip tests
        if 'timed' in str(dberr) or 'connect' in str(dberr):
            print('service unavailable')
            return True
        print('other tvdb exception;', type(dberr), str(dberr))
    except Exception as err:
        print('other exception;', type(err), str(err))
        pass
    # any other issues then we need to continue with testing
    return False


SERVICE_UNAVAILABLE = is_unavailable()


class TvdbServiceTest(base.BaseTest):

    def setUp(self):
        super(TvdbServiceTest, self).setUp()
        self.api = tvdb.TvdbService()

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
    def test_get_series_by_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesname'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_name('Fake - Unknown Series')
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, tvdb_api.tvdb_shownotfound)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
    def test_get_series_by_id(self):
        series, err = self.api.get_series_by_id(80379)
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesname'], 'The Big Bang Theory')

        # defect in version 1.10 tvdb_api due to missing cache% key in the
        # configs of tvdb_api when the actual series not found.
        # series, err = self.api.get_series_by_id(0)
        # self.assertIsNone(series)
        # self.assertIsNotNone(err)
        # self.assertIsInstance(err, tvdb_api.tvdb_error)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
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

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
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

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
    def test_get_episode_name_season_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 2)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvdb_api.tvdb_seasonnotfound)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], '1')
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvdb_api.tvdb_seasonnotfound)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
    def test_get_episode_name_attr_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 'xx')
        self.assertIsNone(episodes)
        self.assertIsNone(eperr)

    @testtools.skipIf(SERVICE_UNAVAILABLE, 'TVDB service unavailable')
    def test_get_episode_name_episode_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [25], 1)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvdb_api.tvdb_episodenotfound)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [15], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Serenity'])
