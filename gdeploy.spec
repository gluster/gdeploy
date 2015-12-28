%define name gdeploy
%define version 1.1
%define release 1
%define gdeploymod ansible/modules/extras/system/glusterfs
%define gdeploytemp /usr/share/ansible/gdeploy
%define gdeploydoc /usr/share/doc/gdeploy

Name:		%{name}
Version:	%{version}
Release:	%{?release}
Summary:	Tool to deploy and manage GlusterFS cluster.

Group:		Applications/System
License:	GPLv3
URL:		http://www.redhat.com/storage
Source0:	%{name}-%{version}.%{release}.tar.gz
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}.%{release}-buildroot
Requires:	ansible >= 1.9 python >= 2.6
%{?el6:Requires: python-argparse}

BuildRequires:  python-setuptools

%description
This package provides ansible modules to setup and configure GluterFS. With
these modules you can:
 Configure backend to setup GlusterFS
  * Setup backend with lvm thinpool support
  * Create Filesystem
  * Mount the filesystem
  * Create and start a GlusterFS volume
  * Mount the clients
 Tool to generate the playbooks, group_vars/host_vars

%prep
%setup -n %{name}-%{version}.%{release}

%build
python setup.py build

%install
# Install the binary and python libraries
rm -rf %{buildroot}
python setup.py install -O1 --root=%{buildroot} --record=INSTALLED_FILES

mkdir -p %{buildroot}/%{python_sitelib}/%{gdeploymod}
install -m 755 modules/* \
    %{buildroot}/%{python_sitelib}/%{gdeploymod}

# Install the templates into /usr/share/ansible/gdeploy/templates
mkdir -p %{buildroot}/%{gdeploytemp}
cp -r templates %{buildroot}/%{gdeploytemp}

# Documentation
mkdir -p %{buildroot}/%{gdeploydoc} %{buildroot}/%{_mandir}/man1/ \
       %{buildroot}/%{_mandir}/man5/
cp -r doc/* README.md examples %{buildroot}/%{gdeploydoc}
cp man/gdeploy.1* %{buildroot}/%{_mandir}/man1/
cp man/gdeploy.conf* %{buildroot}/%{_mandir}/man5/

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%{python_sitelib}/%{gdeploymod}
%{gdeploytemp}

%doc README.md
%docdir %{gdeploydoc}
%{_mandir}/man1/gdeploy*
%{_mandir}/man5/gdeploy*
%{gdeploydoc}

%changelog
* Fri Nov 6 2015 Sachidananda Urs <sac@redhat.com> 1.1
- Patterns in configs are to be tested
- Backend setup config changes(This includes alot)
- Rerunning the config do not throw error
- Backend reset
- Host specific and group specific changes.
- Quota
- Snapshot
- Geo-replication
- Subscription manager
- Package install
- Firewalld
- samba
- CTDB
- CIFS mount

* Mon Aug 3 2015 Sachidananda Urs <sac@redhat.com> 1.0
- Initial release.
