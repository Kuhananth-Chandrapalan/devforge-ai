"""Tests for transient Gemini failures; no live API calls or credentials."""
import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts.free_agent import generate


def response():
    proposal = {'files': [{'path': 'lab/example.py', 'content': 'x = 1\n'}]}
    payload = {'candidates': [{'content': {'parts': [{'text': json.dumps(proposal)}]}}]}
    return io.BytesIO(json.dumps(payload).encode('utf-8'))


def http_error(code):
    return HTTPError('https://example.invalid', code, 'test', {}, None)


class GeminiRetryTests(unittest.TestCase):
    @patch('scripts.free_agent.time.sleep')
    @patch('scripts.free_agent.urlopen')
    def test_503_then_success(self, mocked_open, mocked_sleep):
        mocked_open.side_effect = [http_error(503), response()]
        result = generate('test', 'fake-test-key')
        self.assertEqual(result['files'][0]['path'], 'lab/example.py')
        self.assertEqual(mocked_open.call_count, 2)
        mocked_sleep.assert_called_once_with(8)

    @patch('scripts.free_agent.time.sleep')
    @patch('scripts.free_agent.urlopen')
    def test_503_exhausts_retries(self, mocked_open, mocked_sleep):
        mocked_open.side_effect = [http_error(503) for _ in range(4)]
        with self.assertRaisesRegex(RuntimeError, '503.*4 attempts'):
            generate('test', 'fake-test-key')
        self.assertEqual(mocked_open.call_count, 4)
        self.assertEqual([c.args[0] for c in mocked_sleep.call_args_list], [8, 16, 32])

    @patch('scripts.free_agent.time.sleep')
    @patch('scripts.free_agent.urlopen')
    def test_429_fails_without_retry(self, mocked_open, mocked_sleep):
        mocked_open.side_effect = http_error(429)
        with self.assertRaisesRegex(RuntimeError, 'rate/quota limit'):
            generate('test', 'fake-test-key')
        self.assertEqual(mocked_open.call_count, 1)
        mocked_sleep.assert_not_called()

    @patch('scripts.free_agent.time.sleep')
    @patch('scripts.free_agent.urlopen')
    def test_401_rejected_without_retry(self, mocked_open, mocked_sleep):
        mocked_open.side_effect = http_error(401)
        with self.assertRaisesRegex(RuntimeError, 'access denied'):
            generate('test', 'fake-test-key')
        self.assertEqual(mocked_open.call_count, 1)
        mocked_sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
