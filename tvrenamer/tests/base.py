import logging

from oslo_config import fixture as fixture_config
from oslotest import base as test_base

import tvrenamer
from tvrenamer import options

# see urllib3 regarding InsecureRequestWarning and InsecurePlatformWarning
logging.captureWarnings(True)


class BaseTest(test_base.BaseTestCase):

    def setUp(self):
        super(BaseTest, self).setUp()

        self.CONF = self.useFixture(fixture_config.Config()).conf
        options.register_opts(self.CONF)
        self.CONF([], project=tvrenamer.PROJECT_NAME)
