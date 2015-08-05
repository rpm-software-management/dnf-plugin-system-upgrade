Name:       dnf-plugin-system-upgrade
Version:    0.0.1
Release:    1%{?dist}
Summary:    System Upgrade plugin for DNF
Group:      System Environment/Base
License:    GPLv2+
URL:        https://github.com/rpm-software-management/dnf-plugin-system-upgrade
Source0:    dnf-plugin-system-upgrade-%{version}.tar.gz

Provides:   dnf-command(system-upgrade)

BuildArch:  noarch
# TODO: gettext
BuildRequires: pkgconfig
BuildRequires: systemd

%description
System Upgrade plugin for DNF.
This package provides the systemd services required to make the upgrade work.

# Use the py3 version in F23 and later
%if 0%{?fedora} >= 23
Requires:   python3-dnf-plugin-system-upgrade = %{version}-%{release}
%else
Requires:   python-dnf-plugin-system-upgrade = %{version}-%{release}
%endif

%package -n python3-dnf-plugin-system-upgrade
Summary:    System Upgrade plugin for DNF
Group:      System Environment/Base
Requires:   python3-dnf
BuildRequires:  python3-devel
BuildRequires:  python3-dnf
BuildRequires:  python3-nose
%description -n python3-dnf-plugin-system-upgrade
System Upgrade plugin for DNF (Python 3 version).
This package provides the "system-upgrade" command.

%package -n python-dnf-plugin-system-upgrade
Summary:    System Upgrade plugin for DNF
Group:      System Environment/Base
Requires:   python-dnf
BuildRequires:  python-devel
BuildRequires:  python-dnf
BuildRequires:  python-nose
%description -n python-dnf-plugin-system-upgrade
System Upgrade plugin for DNF (Python 2 version).
This package provides the "system-upgrade" command.

%prep
%setup -q -n dnf-plugin-system-upgrade-%{version}

%build
make install DESTDIR=$RPM_BUILD_ROOT PYTHON=python2
make install DESTDIR=$RPM_BUILD_ROOT PYTHON=python3

%check
make check PYTHON=python2
make check PYTHON=python3

%files
%doc LICENSE README.md
%{_unitdir}/dnf-system-upgrade.service
%{_unitdir}/system-update.target.wants/dnf-system-upgrade.service

%files -n python3-dnf-plugin-system-upgrade
%{python3_sitelib}/dnf-plugins/system_upgrade.py
%{python3_sitelib}/dnf-plugins/__pycache__/system_upgrade*.py*

%files -n python-dnf-plugin-system-upgrade
%{python_sitelib}/dnf-plugins/system_upgrade.py*

%changelog
* Wed Aug 05 2015 Will Woods <wwoods@redhat.com> 0.0.1
- Initial packaging
