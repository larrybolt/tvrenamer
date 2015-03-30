import sqlalchemy as sa

from tvrenamer.cache import models
from tvrenamer.cache import session
from tvrenamer.tests import base


class FakeTable(models.Base, models.HasId, models.HasTimestamp):

    __table_args__ = {
        'sqlite_autoincrement':  True,
    }

    name = sa.Column(sa.String(255))
    val = sa.Column(sa.String(255))


class SAModelsTestCase(base.BaseTest):

    def setUp(self):
        super(SAModelsTestCase, self).setUp()

        self.facade = session.EngineFacade('sqlite:///:memory:')
        models.verify_tables(self.facade.engine)

    def tearDown(self):
        models.purge_all_tables(self.facade.engine)
        super(SAModelsTestCase, self).tearDown()

    def test_base(self):

        self.assertEqual(FakeTable.__tablename__, 'fake_tables')

        _row = FakeTable()
        _row['name'] = 'sample'
        _row['val'] = 'a1234'
        self.assertIsNotNone(_row)
        self.assertIsNotNone(repr(_row))

        self.assertEqual(_row['name'], 'sample')

        for i in _row:
            self.assertIn(i[0],
                          ['id', 'name', 'val', 'created_at', 'updated_at'])

        for k, v in _row.iteritems():
            self.assertIn(k,
                          ['id', 'name', 'val', 'created_at', 'updated_at'])

        values = dict(name='sample1', val='b56789')
        _row.update(values)
        self.assertEqual(_row['name'], 'sample1')

    def test_mediafile(self):
        self.assertEqual(models.MediaFile.__tablename__, 'media_files')
