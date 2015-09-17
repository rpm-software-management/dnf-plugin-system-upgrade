# test_fedup_wrapper.py - unit tests for fedup.sh wrapper script.
#
# (yes, I am using Python to test bash. yes, I am OK with this.)

import unittest
import shlex
from subprocess import Popen, PIPE

BASE_CMD = ['dnf', 'system-upgrade']

def fedup(args, dry_run=True, env=None):
    cmd = ['./fedup.sh']
    if dry_run:
        cmd.append('--dry-run')
    cmd.extend(args)
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, env=env)
    out, err = proc.communicate()
    return out, err, proc.returncode

class FedupTestCase(unittest.TestCase):
    def assert_fedup_equiv(self, fedupargs, dnfargs, in_warnmsg=None):
        out, err, rv = fedup(fedupargs.split(), dry_run=True)
        self.assertEqual(rv, 0)
        self.assertEqual(shlex.split(out.decode()), BASE_CMD+dnfargs.split())
        if in_warnmsg:
            self.assertIn(in_warnmsg, err.decode())

    def assert_fedup_fails(self, fedupargs, in_errmsg=None):
        out, err, rv = fedup(fedupargs.split(), dry_run=True)
        self.assertNotEqual(rv, 0)
        self.assertEqual(out, bytes())
        if in_errmsg:
            self.assertIn(in_errmsg, err.decode())

    def test_none(self):
        self.assert_fedup_equiv("", "")

    def test_ignored(self):
        self.assert_fedup_equiv("--skipbootloader --skipkernel", "")

    def test_network(self):
        self.assert_fedup_equiv("--network=23",
                                "download --releasever=23")

    def test_network_space(self):
        self.assert_fedup_equiv("--network 23",
                                "download --releasever 23")

    def test_ignore_product(self):
        self.assert_fedup_equiv("--network 23 --product=workstation",
                                "download --releasever 23",
                                in_warnmsg="--product")

    def test_ignore_instrepo(self):
        self.assert_fedup_equiv("--network 23 --instrepo FAKE_URL",
                                "download --releasever 23",
                                in_warnmsg="--instrepo")

    def test_disablerepo(self):
        self.assert_fedup_equiv("--network 23 --disablerepo fedora",
                                "download --releasever 23 --disablerepo fedora")

    def test_enablerepo(self):
        self.assert_fedup_equiv("--network 23 --enablerepo=blorp",
                                "download --releasever 23 --enablerepo=blorp")

    def test_network_rawhide(self):
        self.assert_fedup_equiv("--network 23 --nogpgcheck --instrepo URL",
                                "download --releasever 23 --nogpgcheck")

    def test_clean(self):
        self.assert_fedup_equiv("--clean", "clean")

    def test_debuglog(self):
        self.assert_fedup_fails("--debuglog chunkstyle.log")

    def test_bad_args(self):
        badarg = "--mustard=progress"
        self.assert_fedup_fails(badarg, in_errmsg=badarg)

    def test_device(self):
        self.assert_fedup_fails("--device", in_errmsg="dnf system-upgrade")

    def test_conflicting_actions(self):
        self.assert_fedup_fails("--clean --network 23", in_errmsg="clean")
        self.assert_fedup_fails("--clean --network 23", in_errmsg="download")
        self.assert_fedup_fails("reboot --network 23", in_errmsg="reboot")

    def test_clean_metadata(self):
        self.assert_fedup_fails("--clean-metadata", in_errmsg="clean metadata")

    def test_expire_cache(self):
        self.assert_fedup_fails("--expire-cache", in_errmsg="--refresh")

    def test_passthru(self):
        for flag in "--best", "--allowerasing", "--disableplugin=pluggo":
            self.assert_fedup_equiv("--network 23 %s" % flag,
                                    "download --releasever 23 %s" % flag)

    def test_reboot(self):
        self.assert_fedup_equiv("reboot", "reboot")

from test_system_upgrade import I18NTestCaseBase
class I18NTestCase(I18NTestCaseBase):
    def test_fedup_i18n(self):
        msg = "the color of the sky"
        env = dict(
            TEXTDOMAINDIR=self.localedir,
            LC_MESSAGES='en_GB',
        )
        out, _, rv = fedup(["--test-gettext"], env=env)
        self.assertEqual(rv, 0)
        self.assertEqual(out.decode().strip(), self.gettext(msg))
        self.assertNotEqual(self.gettext(msg), msg)

    def test_fedup_i18n_fallback(self):
        msg = "the color of the sky"
        env = dict(
            TEXTDOMAINDIR=self.localedir,
        )
        out, _, rv = fedup(["--test-gettext"], env=env)
        self.assertEqual(rv, 0)
        self.assertEqual(out.decode().strip(), msg)
