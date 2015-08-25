Name:       dnf-plugin-system-upgrade
Version:    0.3.0
Release:    1%{?dist}
Summary:    System Upgrade plugin for DNF
Group:      System Environment/Base
License:    GPLv2+
URL:        https://github.com/rpm-software-management/dnf-plugin-system-upgrade
Source0:    https://github.com/rpm-software-management/dnf-plugin-system-upgrade/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz

Requires: python-%{name}
Provides: dnf-command(system-upgrade)

Provides: fedup
Obsoletes: fedup < 0.9.2-3

BuildArch: noarch
BuildRequires: pkgconfig systemd gettext

%description
System Upgrade plugin for DNF.
This package provides the systemd services required to make the upgrade work.

%package -n python3-%{name}
%{?python_provide:%python_provide python3-%{name}}
Summary:    System Upgrade plugin for DNF
Requires:   python3-dnf
BuildRequires:  python3-devel python3-dnf python3-nose
%description -n python3-%{name}
System Upgrade plugin for DNF (Python 3 version).
This package provides the "system-upgrade" command.

%package -n python2-%{name}
%{?python_provide:%python_provide python2-%{name}}
Summary:    System Upgrade plugin for DNF
BuildRequires: python2-devel python-mock


%if 0%{?fedora} >= 22
BuildRequires:  python2-nose
%else
# Fedora 21 and earlier just call it 'python-nose'
BuildRequires:  python-nose
%endif

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
make install DESTDIR=$RPM_BUILD_ROOT PYTHON=%{__python3}

%check
make check PYTHON=%{__python2}
make check PYTHON=%{__python3}

%files -f %{name}.lang
%license LICENSE
%doc README.md
%{_unitdir}/dnf-system-upgrade.service
%{_unitdir}/system-update.target.wants/dnf-system-upgrade.service
%{_bindir}/fedup

%files -n python3-%{name}
%{python3_sitelib}/dnf-plugins/system_upgrade.py
%{python3_sitelib}/dnf-plugins/__pycache__/system_upgrade*.py*

%files -n python2-%{name}
%{python_sitelib}/dnf-plugins/system_upgrade.py*

%changelog
* Thu Aug 20 2015 Will Woods <wwoods@redhat.com> 0.3.0
- Add `fedup` backward-compatibility wrapper

* Tue Aug 18 2015 Will Woods <wwoods@redhat.com> 0.2.0
- Fix upgrade startup

* Wed Aug 05 2015 Will Woods <wwoods@redhat.com> 0.0.1
- Initial packaging
