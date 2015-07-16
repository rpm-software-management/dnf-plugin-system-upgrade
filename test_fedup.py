# test_fedup.py - unit tests for dnf-plugin-fedup's fedup.py

import fedup

import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from mock import patch
from fedup import PLYMOUTH

@patch('fedup.call', return_value=0)
class PlymouthTestCase(unittest.TestCase):
    def setUp(self):
        self.ply = fedup.PlymouthOutput()
        self.msg = "Hello, plymouth."
        self.msg_args = (PLYMOUTH, "display-message", "--text", self.msg)

    def test_ping(self, call):
        self.ply.ping()
        call.assert_called_once_with((PLYMOUTH, "--ping"))
        self.assertTrue(self.ply.alive)

    def test_ping_when_dead(self, call):
        call.return_value=1
        self.ply.ping()
        self.assertFalse(self.ply.alive)
        call.return_value=0
        self.ply.ping()
        self.assertEqual(call.call_count, 2)
        self.assertTrue(self.ply.alive)

    def test_message(self, call):
        self.ply.message(self.msg)
        call.assert_called_once_with(self.msg_args)

    def test_message_dupe(self, call):
        self.ply.message(self.msg)
        self.ply.message(self.msg)
        call.assert_called_once_with(self.msg_args)

    def test_message_dead(self, call):
        call.return_value = 1
        self.ply.message(self.msg)
        self.assertFalse(self.ply.alive)
        self.ply.message("not even gonna bother")
        call.assert_called_once_with(self.msg_args)

    def test_progress(self, call):
        self.ply.progress(27)
        call.assert_called_once_with((PLYMOUTH, "system-update", "--progress", str(27)))

    def test_mode(self, call):
        self.ply.set_mode("updates")
        call.assert_called_once_with((PLYMOUTH, "change-mode", "--updates"))

@patch('fedup.call', return_value=0)
class PlymouthTransactionDisplayTestCase(unittest.TestCase):
    # pylint: disable=protected-access
    def setUp(self):
        fedup.Plymouth = fedup.PlymouthOutput()
        self.display = fedup.PlymouthTransactionDisplay()
        self.pkg = "testpackage"
        self.action = self.display.PKG_INSTALL

    def test_display(self, call):
        self.display.event(self.pkg, self.action, 0, 100, 1, 1000)
        msg = self.display._fmt_event(self.pkg, self.action, 1, 1000)
        # updating plymouth display means two plymouth calls
        call.assert_has_calls([
                mock.call((PLYMOUTH, "system-update", "--progress", "0")),
                mock.call((PLYMOUTH, "display-message", "--text", msg))
            ], any_order=True)

    def test_filter_calls(self, call):
        # event progress on the same transaction item -> one display update
        for te_current in range(100):
            self.display.event(self.pkg, self.action, te_current, 100, 1, 1000)
        self.assertEqual(call.call_count, 2)
        # next item: new message ("[2/1000] ...") but percentage still 0
        self.display.event(self.pkg, self.action, 0, 100, 2, 1000)
        msg = self.display._fmt_event(self.pkg, self.action, 2, 1000)
        # message was updated..
        call.assert_called_with((PLYMOUTH, "display-message", "--text", msg))
        # ..but no other new calls were made
        self.assertEqual(call.call_count, 3)

    def test_verify(self, call):
        with patch("fedup._", return_value="Verifying"):
            self.display.verify_tsi_package(self.pkg, 1, 1000)
        msg = self.display._fmt_event(self.pkg, "Verifying", 1, 1000)
        call.assert_has_calls([
            mock.call((PLYMOUTH, "system-update", "--progress", "0")),
            mock.call((PLYMOUTH, "display-message", "--text", msg))
        ], any_order=True)
