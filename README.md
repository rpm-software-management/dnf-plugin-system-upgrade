# dnf-plugin-system-upgrade

A plugin for [DNF] that does [fedup]-style upgrades using [systemd]'s [Offline
Updates] facility.

## Installation

    make install

## Example Usage

    dnf system-upgrade download --releasever=22
    dnf system-upgrade reboot

[DNF]: https://github.com/rpm-software-management/dnf
[fedup]: https://github.com/rhinstaller/fedup
[systemd]: https://github.com/systemd/systemd
[Offline Updates]: http://www.freedesktop.org/wiki/Software/systemd/SystemUpdates/
