#!/bin/sh
# wrapper script to call `dnf system-upgrade` instead

# fix --network -> download --releasever, since we can't do that in the plugin
set -- "$@" END_OF_OPTIONS
while [ "$1" != END_OF_OPTIONS ]; do
    case "$1" in
        --network*) set -- "$@" download "${1/--network/--releasever}" ;;
        *)          set -- "$@" "$1" ;;
    esac
    shift
done
shift

exec /usr/bin/dnf system-upgrade "$@"
