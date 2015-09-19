from __future__ import print_function

import mock

from tvrenamer.processors import printer
from tvrenamer.tests import base


class PrintProcessorTests(base.BaseTest):

    def setUp(self):
        super(PrintProcessorTests, self).setUp()
        self.CONF.set_override('cron', False)
        self.processor = printer.PrintResults()

    def _make_data(self):
        results = []
        ep1 = mock.Mock()
        ep1.status = {
            '/tmp/Lucy.2014.576p.BDRip.AC3.x264.DuaL-EAGLE.mkv': {
                'formatted_filename': None,
                'state': 'failed',
                'messages': 'Could not find season 20'}
            }
        results.append(ep1)

        ep2 = mock.Mock()
        ep2.status = {
            '/tmp/revenge.412.hdtv-lol.mp4': {
                'formatted_filename': 'S04E12-Madness.mp4',
                'state': 'finished',
                'messages': None}
            }
        results.append(ep2)
        return results

    @mock.patch.object(printer.LOG, 'isEnabledFor')
    def test_print_results(self, mock_log):

        mock_log.return_value = False
        self.assertFalse(self.processor.enabled)

        with mock.patch.object(printer.table, 'write_output') as mock_output:
            self.processor.process([])
            self.assertFalse(mock_output.called)

        mock_log.return_value = True
        self.assertTrue(self.processor.enabled)

        with mock.patch.object(printer.table, 'write_output') as mock_output:
            self.processor.process([])
            self.assertFalse(mock_output.called)

        with mock.patch('six.moves.builtins.print') as mock_print:
            self.processor.process(self._make_data())
            self.assertTrue(mock_print.called)
