# dnf-plugin-fedup

fedup is back.. in DNF plugin form!!

## Installation

    make install
    systemctl enable fedup-system-upgrade.service

## Usage

    dnf fedup download --releasever=22
    dnf fedup reboot

## Bugs

Upstream DNF doesn't have any way for plugins to modify the transaction
progress display, so the plugin can't update the plymouth status messages.

This patch adds support: wgwoods/dnf@e18101bac6b1a76afe005807600fc7fcd128f894
