Name:       dnf-plugin-system-upgrade
Version:    0.4.1
Release:    1%{?dist}
Summary:    System Upgrade plugin for DNF
Group:      System Environment/Base
License:    GPLv2+
URL:        https://github.com/rpm-software-management/dnf-plugin-system-upgrade
Source0:    https://github.com/rpm-software-management/dnf-plugin-system-upgrade/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

%if 0%{?fedora} >= 23
# DNF in Fedora 23 uses Python 3 by default
Requires: python3-%{name}
Requires: python3-systemd
%else
Requires: python2-%{name}
Requires: python-systemd
%endif

Provides: dnf-command(system-upgrade)

# The plugin itself doesn't technically require dnf, but /usr/bin/fedup does.
# So either we split out a subpackage for /usr/bin/fedup or we Require dnf.
Requires: dnf

Provides: fedup = 0.9.3-1
Obsoletes: fedup < 0.9.3-1

%if 0%{?fedora} == 21
# Fedora 21 has the necessary fixes backported to 1.0.6-2
Conflicts: PackageKit < 1.0.6-2
%else
Conflicts: PackageKit < 1.0.8
%endif

BuildArch: noarch
BuildRequires: pkgconfig systemd gettext

%description
System Upgrade plugin for DNF.
This package provides the systemd services required to make the upgrade work.

%package -n python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:    System Upgrade plugin for DNF
Requires:   python3-dnf
BuildRequires:  python3-devel python3-dnf
%description -n python3-%{name}
System Upgrade plugin for DNF (Python 3 version).
This package provides the "system-upgrade" command.

%package -n python2-%{name}
%{?python_provide:%python_provide python2-%{name}}
Summary:    System Upgrade plugin for DNF
BuildRequires: python2-devel python-mock


%if 0%{?fedora} >= 22
# TODO: update this once dnf is following the Python packaging guidelines
Requires:       python-dnf
BuildRequires:  python-dnf
%else
# F21 didn't split out python2-dnf from the main dnf package
Requires:       dnf
BuildRequires:  dnf
%endif

%description -n python2-%{name}
System Upgrade plugin for DNF (Python 2 version).
This package provides the "system-upgrade" command.

%prep
%setup -q -n %{name}-%{version}

%build
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT PYTHON=%{__python2}
%find_lang %{name}
make install-plugin DESTDIR=$RPM_BUILD_ROOT PYTHON=%{__python3}

%check
make check PYTHON=%{__python2}
make check PYTHON=%{__python3}

%pre
# if we're replacing fedup, we need to make sure it cleans up its leftovers.
# (see https://bugzilla.redhat.com/show_bug.cgi?id=1264948)
if [ "$1" == 1 -a -x /usr/bin/fedup ]; then
    # save the old package cache (if the new one isn't populated)
    if [ -d /var/lib/system-upgrade ]; then
        mv -f -T /var/lib/system-upgrade /var/lib/dnf/system-upgrade || :
    fi
    # clean up everything else
    /usr/bin/fedup --clean || :
fi

%files -f %{name}.lang
%license LICENSE
%doc README.md
%{_mandir}/man8/dnf.plugin.system-upgrade.8*
%{_mandir}/man8/fedup.8*
%{_unitdir}/dnf-system-upgrade.service
%dir %{_unitdir}/system-update.target.wants
%{_unitdir}/system-update.target.wants/dnf-system-upgrade.service
%{_bindir}/fedup

%files -n python3-%{name}
%license LICENSE
%{python3_sitelib}/dnf-plugins/system_upgrade.py
%{python3_sitelib}/dnf-plugins/__pycache__/system_upgrade*.py*

%files -n python2-%{name}
%license LICENSE
%{python_sitelib}/dnf-plugins/system_upgrade.py*

%changelog
* Tue Sep 15 2015 Will Woods <wwoods@redhat.com> 0.4.1-1
- Fix `dnf system-upgrade clean` (rhbz#1262145)
- Fix duplicate messages in plymouth 'details' output (github#13)
- Add man pages dnf.plugin.system-upgrade(8) and fedup(8)

* Wed Sep 09 2015 Kalev Lember <klember@redhat.com> 0.4.0-2
- Conflict with older PackageKit versions that didn't let other programs do
  offline updates (#1259937)
- Pull in the Python 3 version of the DNF plugin on Fedora 23 (#1260164)

* Mon Aug 31 2015 Will Woods <wwoods@redhat.com> 0.4.0-1
- Meet Fedora packaging requirements
- Add translations to `fedup` wrapper

* Thu Aug 20 2015 Will Woods <wwoods@redhat.com> 0.3.0-1
- Add `fedup` backward-compatibility wrapper

* Tue Aug 18 2015 Will Woods <wwoods@redhat.com> 0.2.0-1
- Fix upgrade startup

* Wed Aug 05 2015 Will Woods <wwoods@redhat.com> 0.0.1-1
- Initial packaging
