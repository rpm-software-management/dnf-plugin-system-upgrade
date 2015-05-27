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

This patch adds support: https://github.com/wgwoods/dnf/commit/e18101b
