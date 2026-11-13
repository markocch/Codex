import io
import json
import unittest
from unittest.mock import Mock
from urllib.error import HTTPError
from meta_ads.ga4 import GA4Client, GA4Error, report_body


class GA4Tests(unittest.TestCase):
    def test_dates(self):
        for start, end in [('2026-02-30', '2026-03-01'), ('2026-12-01', '2026-01-01')]:
            with self.assertRaises(GA4Error):
                report_body(start, end)

    def test_paginated_read_report(self):
        opener = Mock()
        opener.open.side_effect = [io.BytesIO(json.dumps(r).encode()) for r in (
            {'rows': [{'dimensionValues': [{'value': 'Groomer'}]}], 'rowCount': 2},
            {'rows': [{'dimensionValues': [{'value': 'Iddeale'}]}], 'rowCount': 2})]
        result = GA4Client('private-token', opener).report('123', '2026-01-01', '2026-01-31')
        self.assertEqual(len(result['rows']), 2)
        for call in opener.open.call_args_list:
            req = call.args[0]
            self.assertEqual(req.get_method(), 'POST')
            self.assertEqual(req.full_url, 'https://analyticsdata.googleapis.com/v1beta/properties/123:runReport')
            self.assertNotIn('private-token', req.full_url)
            self.assertEqual(req.get_header('Authorization'), 'Bearer private-token')
        self.assertEqual(json.loads(opener.open.call_args.args[0].data)['offset'], '1')

    def test_property_rejected_before_network(self):
        opener = Mock()
        with self.assertRaises(GA4Error):
            GA4Client('secret', opener).report('G-ABC', '2026-01-01', '2026-01-02')
        opener.open.assert_not_called()

    def test_error_redacted(self):
        opener = Mock()
        opener.open.side_effect = HTTPError('secret', 403, 'secret', {}, io.BytesIO(b'secret'))
        with self.assertRaises(GA4Error) as error:
            GA4Client('secret', opener).report('123', '2026-01-01', '2026-01-02')
        self.assertNotIn('secret', str(error.exception))

    def test_empty_result(self):
        opener = Mock()
        opener.open.return_value = io.BytesIO(b'{}')
        self.assertEqual(GA4Client('secret', opener).report('123', '2026-01-01', '2026-01-02')['rows'], [])
