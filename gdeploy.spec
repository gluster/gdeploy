%define name gdeploy
%define version 1
%define release 1
%define gdeploymod ansible/modules/extras/system/glusterfs
%define gdeploytemp /usr/share/ansible/gdeploy
%define gdeploydoc /usr/share/doc/ansible/gdeploy

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

BuildRequires:  python-setuptools

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
mkdir -p %{buildroot}/%{gdeploydoc}
cp -r README.md examples %{buildroot}/%{gdeploydoc}

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%{python_sitelib}/%{gdeploymod}
%{gdeploytemp}

%doc README.md
%docdir %{gdeploydoc}
%{gdeploydoc}

%changelog
* Tue Aug 18 2015 Sachidananda Urs <sac@redhat.com> 1.1
- Major changes to rebalance.

* Mon Aug 3 2015 Sachidananda Urs <sac@redhat.com> 1.0
- Initial release.
