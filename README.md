# dnf-plugin-fedup

A proof-of-concept plugin for [DNF] that shows how to do [fedup]-style upgrades
using [systemd]'s [Offline Updates] facility.

## Installation

    make install

## Usage

    dnf fedup download --releasever=22
    dnf fedup reboot

[DNF]: https://github.com/rpm-software-management/dnf
[fedup]: https://github.com/rhinstaller/fedup
[systemd]: https://github.com/systemd/systemd
[Offline Updates]: http://www.freedesktop.org/wiki/Software/systemd/SystemUpdates/
