#!/bin/sh
# wrapper script to call `dnf system-upgrade` instead

exec /usr/bin/dnf system-upgrade "$@"
