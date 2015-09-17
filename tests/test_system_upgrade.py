# test_system_upgrade.py - unit tests for system-upgrade plugin

import system_upgrade

import unittest
try:
    from unittest import mock
except ImportError:
    import mock
patch = mock.patch

from system_upgrade import PLYMOUTH


@patch('system_upgrade.call', return_value=0)
class PlymouthTestCase(unittest.TestCase):
    def setUp(self):
        self.ply = system_upgrade.PlymouthOutput()
        self.msg = "Hello, plymouth."
        self.msg_args = (PLYMOUTH, "display-message", "--text", self.msg)

    def test_ping(self, call):
        self.ply.ping()
        call.assert_called_once_with((PLYMOUTH, "--ping"))
        self.assertTrue(self.ply.alive)

    def test_ping_when_dead(self, call):
        call.return_value = 1
        self.ply.ping()
        self.assertFalse(self.ply.alive)
        call.return_value = 0
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
        call.assert_called_once_with(
            (PLYMOUTH, "system-update", "--progress", str(27)))

    def test_mode(self, call):
        self.ply.set_mode("updates")
        call.assert_called_once_with((PLYMOUTH, "change-mode", "--updates"))

from dnf.callback import (PKG_CLEANUP, PKG_DOWNGRADE, PKG_INSTALL, PKG_OBSOLETE,
                          PKG_REINSTALL, PKG_REMOVE, PKG_UPGRADE, PKG_VERIFY,
                          TRANS_POST)

@patch('system_upgrade.call', return_value=0)
class PlymouthTransactionProgressTestCase(unittest.TestCase):
    actions = (PKG_CLEANUP, PKG_DOWNGRADE, PKG_INSTALL, PKG_OBSOLETE,
               PKG_REINSTALL, PKG_REMOVE, PKG_UPGRADE, PKG_VERIFY,
               TRANS_POST)
    # pylint: disable=protected-access
    def setUp(self):
        system_upgrade.Plymouth = system_upgrade.PlymouthOutput()
        self.display = system_upgrade.PlymouthTransactionProgress()
        self.pkg = "testpackage"

    def test_display(self, call):
        for action in self.actions:
            self.display.progress(self.pkg, action, 0, 100, 1, 1000)
            msg = self.display._fmt_event(self.pkg, action, 1, 1000)
            # updating plymouth display means two plymouth calls
            call.assert_has_calls([
                mock.call((PLYMOUTH, "system-update", "--progress", "0")),
                mock.call((PLYMOUTH, "display-message", "--text", msg))
            ], any_order=True)

    def test_filter_calls(self, call):
        action = PKG_INSTALL
        # event progress on the same transaction item -> one display update
        for te_cur in range(100):
            self.display.progress(self.pkg, action, te_cur, 100, 1, 1000)
        self.assertEqual(call.call_count, 2)
        # next item: new message ("[2/1000] ...") but percentage still 0
        self.display.progress(self.pkg, action, 0, 100, 2, 1000)
        msg = self.display._fmt_event(self.pkg, action, 2, 1000)
        # message was updated..
        call.assert_called_with((PLYMOUTH, "display-message", "--text", msg))
        # ..but no other new calls were made
        self.assertEqual(call.call_count, 3)

import os, tempfile, shutil, gettext
@unittest.skipUnless(os.path.exists("po/en_GB.mo"), "make po/en_GB.mo first")
class I18NTestCaseBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.localedir = tempfile.mkdtemp(prefix='i18ntest')
        cls.msgdir = os.path.join(cls.localedir, "en_GB/LC_MESSAGES")
        cls.msgfile = system_upgrade.TEXTDOMAIN + ".mo"
        os.makedirs(cls.msgdir)
        shutil.copy2("po/en_GB.mo",
                     os.path.join(cls.msgdir, cls.msgfile))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.localedir)

    def setUp(self):
        self.t = gettext.translation(system_upgrade.TEXTDOMAIN, self.localedir,
                                languages=["en_GB"], fallback=True)
        self.gettext = self.t.gettext

class I18NTestCase(I18NTestCaseBase):
    def test_selftest(self):
        self.assertIn(self.msgfile, os.listdir(self.msgdir))
        self.assertIn("en_GB", os.listdir(self.localedir))
        t = gettext.translation(system_upgrade.TEXTDOMAIN, self.localedir,
                                languages=["en_GB"], fallback=False)
        info = t.info()
        self.assertIn("language", info)
        self.assertEqual(info["language"], "en-GB")

    def test_fallback(self):
        msg = "THIS STRING DOES NOT EXIST"
        trans_msg = self.gettext(msg)
        self.assertEqual(msg, trans_msg)

    def test_translation(self):
        msg = "the color of the sky"
        trans_msg = self.gettext(msg)
        self.assertNotEqual(msg, trans_msg)

class ArgparseTestCase(unittest.TestCase):
    def test_actions_exist(self):
        for phase in ('configure', 'run'):
            for action in system_upgrade.ACTIONS:
                fn = phase + '_' + action
                func = getattr(system_upgrade.SystemUpgradeCommand, fn)
                self.assertTrue(callable(func))

class StateTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.statedir = tempfile.mkdtemp(prefix="state.test.")
        cls.StateClass = system_upgrade.State
        cls.StateClass.statefile = os.path.join(cls.statedir, "state")

    def setUp(self):
        self.state = self.StateClass()

    def test_set_write_get(self):
        path = "/some/stupid/path"
        with self.state:
            self.state.datadir = path
        del self.state
        self.state = self.StateClass()
        self.assertEqual(self.state.datadir, path)

    def test_clear(self):
        self.state.clear()
        del self.state
        self.state = self.StateClass()
        self.assertIs(self.state.datadir, None)

    def test_bool_value(self):
        with self.state:
            self.state.distro_sync = True
        del self.state
        self.state = self.StateClass()
        self.assertIs(self.state.distro_sync, True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.statedir)

class UtilTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='util.test.')
        self.dirs = ["dir1", "dir2"]
        self.files = ["file1", "dir2/file2"]
        for d in self.dirs:
            os.makedirs(os.path.join(self.tmpdir, d))
        for f in self.files:
            with open(os.path.join(self.tmpdir, f), 'wt') as fobj:
                fobj.write("hi there\n")

    def test_self_test(self):
        for d in self.dirs:
            self.assertTrue(os.path.isdir(os.path.join(self.tmpdir, d)))
        for f in self.files:
            self.assertTrue(os.path.exists(os.path.join(self.tmpdir, f)))

    def test_clear_dir(self):
        self.assertTrue(os.path.isdir(self.tmpdir))
        system_upgrade.clear_dir(self.tmpdir)
        self.assertTrue(os.path.isdir(self.tmpdir))
        self.assertEqual(os.listdir(self.tmpdir), [])

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
