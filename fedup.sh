#!/bin/bash
# wrapper script to rewrite fedup options for `dnf system-upgrade`
#
# Copyright (c) 2015 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Will Woods <wwoods@redhat.com>

export TEXTDOMAIN="dnf-plugin-system-upgrade"
export TEXTDOMAINDIR="${TEXTDOMAINDIR:-/usr/share/locale}"

PROG=${0##*/}
warn() {
    local prefix="$(gettext warning:)" fmt="$1"; shift
    printf "$PROG: $prefix $fmt\\n" "$@" >&2
}

error() {
    local prefix="$(gettext error:)" fmt="$1"; shift
    printf "$PROG: $prefix $fmt\\n" "$@" >&2
    exit 1
}

quote_word() {
    local numwords=$#; set -- $*
    [ $numwords == $# ] && echo "$*" || echo "\"$*\""
}
quote_line() {
    local line=$(while [ $# -gt 0 ]; do quote_word "$1"; shift; done)
    echo $line
}

DEPRECATED_MSG=$(gettext "fedup has been replaced by 'dnf system-upgrade'. Use that instead.")
echo "$DEPRECATED_MSG" >&2

BASECMD="dnf system-upgrade"
dry_run=0
action=''
ACTION_ERR_MSG=$(gettext "Can't do --network and --clean at the same time.")

dnf_cmd=($BASECMD)

while [ $# -gt 0 ]; do
    flag="${1%%=*}"
    case "$flag" in
        # pass through to DNF
        -h|--help|-v|--verbose|-d|--debug|-C|--cacheonly|--nogpgcheck)
            dnf_cmd+=("$1")
        ;;
        # pass through to DNF, with argument
        --enablerepo|--disablerepo)
            dnf_cmd+=("$1")
            [[ "$1" != *=* ]] && shift && dnf_cmd+=("$1")
        ;;
        # ignore deprecated args
        --skipbootloader|--skipkernel|--resetbootloader)
            warnmsg=$(gettext "'%s' is not used anymore. ignoring.")
            warn "$warnmsg" $flag
        ;;
        # ignore deprecated args that take arguments
        --instrepo*|--product)
            warnmsg=$(gettext "'%s' is not used anymore. ignoring.")
            warn "$warnmsg" $flag
            [[ "$1" != *=* ]] && shift
        ;;
        # silently ignore old debugging options
        --skippkgs|--logtraceback)
            : # do nothing
        ;;
        # removed options. these cause errors.
        --debuglog)
            errmsg=$(gettext "Can't redirect DNF logs. Use DNF debug options instead.")
            error "$errmsg"
        ;;
        --enableplugin|--disableplugin)
            errmsg=$(gettext "Sorry, dnf doesn't support '%s'")
            error "$errmsg" $flag
        ;;
        --device|--iso|--add-install)
            errmsg=$(gettext "Sorry, dnf system-upgrade doesn't support '%s'")
            error "$errmsg" $flag
        ;;
        --expire-cache)
            errmsg=$(gettext "'--expire-cache' removed. Use 'dnf system-upgrade download --refresh'")
            error "$errmsg"
        ;;
        --clean-metadata)
            errmsg=$(gettext "'--clean-metadata' removed. Use 'dnf clean metadata --releasever=VER'")
            error "$errmsg"
        ;;
        # --network became --releasever, basically
        --network)
            [ "$action" == "clean" ] && error "$ACTION_ERR_MSG"
            action="download"
            newarg="${1/--network/--releasever}"
            dnf_cmd+=("download" "$newarg")
            [[ "$1" != *=* ]] && shift && dnf_cmd+=("$1")
        ;;
        # --clean is now the "clean" command
        --clean)
            [ "$action" == "download" ] && error "$ACTION_ERR_MSG"
            action="clean"
            dnf_cmd+=("clean")
        ;;
        # like with `make -n`, just print what would have been executed
        -n|--dry-run|--just-print)
            dry_run=1
        ;;
        # for testing purposes only
        --test-gettext)
            echo $(gettext "the color of the sky") && exit 0
        ;;
        # unknown argument
        *)
            errmsg=$(gettext "unknown argument '%s'")
            error "$errmsg" "$1"
        ;;
    esac
    shift
done

dnf_cmd_quoted=$(quote_line "${dnf_cmd[@]}")

if [ $dry_run == 1 ]; then
    echo $dnf_cmd_quoted
    exit 0
fi

redir_msg=$(gettext "Redirecting to '%s':")
printf "$redir_msg\\n" "$dnf_cmd_quoted"
exec "${dnf_cmd[@]}"
