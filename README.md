# dnf-plugin-system-upgrade

A plugin for [DNF] that does [fedup]-style upgrades using [systemd]'s [Offline
Updates] facility.

## Installation

    make install

## Example Usage

To download everything needed to upgrade to Fedora 23:

    # dnf system-upgrade download --releasever=23

Once that finishes, you can begin the upgrade process:

    # dnf system-upgrade reboot

There's also a `fedup`-compatible wrapper script, so this works too:

    # fedup --network 23
    # fedup reboot

## Testing Tips

#### Finding upgrade logs

Everything printed by `dnf` during the upgrade is in the system journal.
Use `journalctl --list-boots` to show a list of system boots, and
`journalctl -b -[NUM]` to display the log that corresponds to the upgrade.

#### Enable debug shell on `/dev/tty9`

If you'd like a root shell available during the upgrade, add
`systemd.debug-shell` to your boot arguments.

You can also enable the shell for all system updates/upgrades:

    # systemctl add-wants system-update.target debug-shell.service

Switch to the shell with <kbd>Ctrl-Alt-F9</kbd> and back to the upgrade progress with <kbd>Ctrl-Alt-F1</kbd>.

#### In case of boot problems

If the system gets stuck at `system-update.target` without starting the
upgrade, remove `/system-update` to make the system boot normally.


If you don't have the debug shell available, you can use the dracut emergency
shell; add `rd.break` to the boot args, then:

    # mount -o remount,rw /sysroot
    # rm /sysroot/system-update

 Exit the shell and your system should start normally.

[DNF]: https://github.com/rpm-software-management/dnf
[fedup]: https://github.com/rhinstaller/fedup
[systemd]: https://github.com/systemd/systemd
[Offline Updates]: http://www.freedesktop.org/wiki/Software/systemd/SystemUpdates/
