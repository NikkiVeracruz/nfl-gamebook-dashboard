"""Offline regression coverage for bounded NFL watchdog feed retries."""
import io
import json
import unittest
from unittest.mock import patch, call
from urllib.error import HTTPError

import nfl_update_watchdog as watchdog


def http_error(code):
    return HTTPError(watchdog.FEED_URL, code, "test error", {}, io.BytesIO())


class FeedRetryTests(unittest.TestCase):
    def setUp(self):
        self.feed = {"games": [], "updated_at": "2026-11-24T05:00:00Z"}

    def response(self):
        return io.BytesIO(json.dumps(self.feed).encode())

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_success_does_not_retry(self, fetch, sleep):
        fetch.return_value = self.response()
        self.assertEqual(watchdog.read_feed(), self.feed)
        self.assertEqual(fetch.call_count, 1)
        sleep.assert_not_called()

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_transient_503_recovers_on_second_attempt(self, fetch, sleep):
        fetch.side_effect = [http_error(503), self.response()]
        self.assertEqual(watchdog.read_feed(), self.feed)
        self.assertEqual(fetch.call_count, 2)
        sleep.assert_called_once_with(5)

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_transient_errors_recover_on_third_attempt(self, fetch, sleep):
        fetch.side_effect = [http_error(502), http_error(504), self.response()]
        self.assertEqual(watchdog.read_feed(), self.feed)
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(5), call(15)])

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_persistent_503_raises_and_stops(self, fetch, sleep):
        fetch.side_effect = [http_error(503) for _ in range(3)]
        with self.assertRaises(HTTPError) as raised:
            watchdog.read_feed()
        self.assertEqual(raised.exception.code, 503)
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(5), call(15)])

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_nontransient_http_errors_fail_immediately(self, fetch, sleep):
        for code in (401, 403, 404, 429):
            with self.subTest(code=code):
                fetch.reset_mock()
                fetch.side_effect = http_error(code)
                with self.assertRaises(HTTPError):
                    watchdog.read_feed()
                self.assertEqual(fetch.call_count, 1)
        sleep.assert_not_called()

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_invalid_json_not_retried(self, fetch, sleep):
        fetch.return_value = io.BytesIO(b"not JSON")
        with self.assertRaises(json.JSONDecodeError):
            watchdog.read_feed()
        self.assertEqual(fetch.call_count, 1)
        sleep.assert_not_called()

    @patch.object(watchdog.time, "sleep")
    @patch.object(watchdog.urllib.request, "urlopen")
    def test_oversized_feed_not_retried(self, fetch, sleep):
        fetch.return_value = io.BytesIO(b"x" * 2_000_001)
        with self.assertRaises(ValueError):
            watchdog.read_feed()
        self.assertEqual(fetch.call_count, 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
