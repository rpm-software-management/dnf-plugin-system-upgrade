# dnf-plugin-system-upgrade

A plugin for [DNF] that does [fedup]-style upgrades using [systemd]'s [Offline
Updates] facility.

## Installation

    make install

## Example Usage

To download everything needed to upgrade to Fedora 23:

    dnf system-upgrade download --releasever=23


Once that finishes, you can begin the upgrade process:

    dnf system-upgrade reboot

## Testing Tips

#### Enable debug shell on `/dev/tty9`

    systemctl add-wants system-update.target debug-shell.service

#### In case of boot problems

If the system gets stuck at `system-update.target` without starting the
upgrade, remove `/system-update` to make the system boot normally.


If you don't have the debug shell available, you can use the dracut emergency
shell; add `rd.break` to the boot args, then:

    mount -o remount,rw /sysroot
    rm /sysroot/system-update

[DNF]: https://github.com/rpm-software-management/dnf
[fedup]: https://github.com/rhinstaller/fedup
[systemd]: https://github.com/systemd/systemd
[Offline Updates]: http://www.freedesktop.org/wiki/Software/systemd/SystemUpdates/
