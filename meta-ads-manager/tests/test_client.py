import io
import json
import unittest
from unittest.mock import Mock
from urllib.error import HTTPError
from meta_ads.client import MetaClient, MetaError, NoRedirect


class ClientTests(unittest.TestCase):
    def client(self, *responses):
        opener = Mock()
        opener.open.side_effect = [io.BytesIO(json.dumps(r).encode()) for r in responses]
        return MetaClient('test-secret', opener), opener

    def test_get_and_authorization(self):
        client, opener = self.client({'id': '123'})
        self.assertEqual(client.get('act_123', fields='id'), {'id': '123'})
        req = opener.open.call_args.args[0]
        self.assertEqual(req.get_method(), 'GET')
        self.assertEqual(req.get_header('Authorization'), 'Bearer test-secret')
        self.assertNotIn('test-secret', req.full_url)

    def test_pagination_does_not_follow_external_url(self):
        client, opener = self.client(
            {'data': [1], 'paging': {'next': 'https://evil.example/?access_token=secret', 'cursors': {'after': 'a'}}},
            {'data': [2]})
        self.assertEqual(list(client.pages('act_123/campaigns')), [1, 2])
        self.assertTrue(all(c.args[0].full_url.startswith('https://graph.facebook.com/v26.0/')
                            for c in opener.open.call_args_list))
        self.assertIn('after=a', opener.open.call_args.args[0].full_url)

    def test_repeated_cursor_fails(self):
        page = {'data': [], 'paging': {'next': 'ignored', 'cursors': {'after': 'a'}}}
        client, _ = self.client(page, page)
        with self.assertRaises(MetaError):
            list(client.pages('act_123/campaigns'))

    def test_error_does_not_expose_secret(self):
        client, opener = self.client()
        opener.open.side_effect = HTTPError('url', 401, 'test-secret', {},
            io.BytesIO(b'{"error":{"code":190,"message":"test-secret"}}'))
        with self.assertRaises(MetaError) as error:
            client.get('act_123')
        self.assertNotIn('test-secret', str(error.exception))
        self.assertIn('190', str(error.exception))

    def test_report_preserves_campaign_without_metrics(self):
        client, opener = self.client({'currency': 'BRL'}, {'data': [
            {'id': '1', 'name': 'A'}, {'id': '2', 'name': 'B'}]},
            {'data': [{'campaign_id': '1', 'spend': '12.00'}]})
        result = client.report()
        self.assertEqual(result['campaigns'][0]['insights']['spend'], '12.00')
        self.assertIsNone(result['campaigns'][1]['insights'])
        self.assertTrue(all(c.args[0].get_method() == 'GET' for c in opener.open.call_args_list))

    def test_rejects_invalid_account_and_paths(self):
        client, opener = self.client()
        for path in ('https://evil.example', '../me', 'me?access_token=x'):
            with self.assertRaises(MetaError):
                client.get(path)
        with self.assertRaises(MetaError):
            client.report('me')
        opener.open.assert_not_called()

    def test_redirects_disabled(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.example'))


if __name__ == '__main__':
    unittest.main()
