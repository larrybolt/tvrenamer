import logging
import mock

from tvrenamer.cache import session
from tvrenamer.tests import base


class EngineFacadeTestCase(base.BaseTest):

    def setUp(self):
        super(EngineFacadeTestCase, self).setUp()

        self.facade = session.EngineFacade('sqlite://')

    def test_get_engine(self):
        eng1 = self.facade.engine
        eng2 = self.facade.engine

        self.assertIs(eng1, eng2)

    def test_get_session(self):
        ses1 = self.facade.session
        ses2 = self.facade.session

        self.assertIsNot(ses1, ses2)

    def test_get_session_maker(self):
        sm1 = self.facade.session_maker
        sm2 = self.facade.session_maker

        self.assertIs(sm1, sm2)

    def test_create_engine(self):

        session.create_engine('sqlite:///:memory:')
        self.assertEqual(
            logging.getLogger('sqlalchemy.engine').getEffectiveLevel(),
            logging.WARNING)

        session.create_engine('sqlite:///:memory:',
                              connection_debug=50)
        self.assertEqual(
            logging.getLogger('sqlalchemy.engine').getEffectiveLevel(),
            logging.INFO)

        session.create_engine('sqlite:///:memory:',
                              connection_debug=100)
        self.assertEqual(
            logging.getLogger('sqlalchemy.engine').getEffectiveLevel(),
            logging.DEBUG)

    @mock.patch('tvrenamer.cache.session.get_maker')
    @mock.patch('tvrenamer.cache.session.create_engine')
    def test_creation_from_config(self, create_engine, get_maker):
        conf = mock.MagicMock()
        conf.cache.items.return_value = [
            ('connection_debug', 100),
        ]

        session.EngineFacade.from_config('sqlite:///:memory:', conf)

        conf.cache.items.assert_called_once_with()
        create_engine.assert_called_once_with(
            sql_connection='sqlite:///:memory:',
            connection_debug=100,
            idle_timeout=mock.ANY,
        )
        get_maker.assert_called_once_with(engine=create_engine())
