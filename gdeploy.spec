%global gdeploymod ansible/modules/extras/system/glusterfs
%global gdeploytemp %{_datadir}/gdeploy

Name:           gdeploy
Version:        2.0.1
Release:        4
Summary:        Tool to deploy and manage GlusterFS cluster

License:        GPLv2
URL:            https://github.com/gluster/gdeploy
Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       ansible >= 2.1
Requires:       python2
Requires:       python2-ecdsa
Requires:       python-markupsafe
Requires:       python2-crypto
Requires:       lvm2
Requires:       PyYAML
Requires:       python2-jinja2
Requires:       python2-paramiko

BuildRequires:  python2-setuptools
BuildRequires:  python2-devel

%description
gdeploy is an Ansible based deployment tool. Initially gdeploy was written to
install GlusterFS clusters, eventually it grew out to do lot of other things. On
a given set of hosts, gdeploy can create physical volumes, volume groups, and
logical volumes, install packages, subscribe to RHN channels, run shell
commands, create GlusterFS volumes and more.

See http://gdeploy.readthedocs.io/en/latest/ for more details

%prep
%autosetup

%build
%{__python2} setup.py build

%install
# Install the binary and python libraries
%{__python2} setup.py install -O1 --root=%{buildroot} --install-scripts %{_bindir}

mkdir -p %{buildroot}/%{python2_sitelib}/%{gdeploymod}
install -p -m 755 modules/* \
    %{buildroot}/%{python2_sitelib}/%{gdeploymod}

# Install the playbooks into /usr/share/gdeploy/playbooks
mkdir -p %{buildroot}/%{gdeploytemp}
cp -rp playbooks %{buildroot}/%{gdeploytemp}

# Install scripts
cp -rp extras/scripts %{buildroot}/%{gdeploytemp}

# Install usecases
cp -rp extras/usecases %{buildroot}/%{gdeploytemp}

# Install the script to /usr/bin
mkdir -p %{buildroot}/usr/bin
install -p -m 755 extras/usecases/replace-node/gluster-replace-node \
        %{buildroot}/usr/bin

# Documentation
mkdir -p %{buildroot}/%{_pkgdocdir} %{buildroot}/%{_mandir}/man1/ \
       %{buildroot}/%{_mandir}/man5/
cp -rp docs/* examples %{buildroot}/%{_pkgdocdir}
cp -p man/gdeploy.1* %{buildroot}/%{_mandir}/man1/
cp -p man/gdeploy.conf* %{buildroot}/%{_mandir}/man5/

%files
%{_bindir}/gdeploy
%{python2_sitelib}/*
%{gdeploytemp}
%{_bindir}/gluster-replace-node

%doc README.md
%doc %{_pkgdocdir}/*
%{_mandir}/man1/gdeploy*
%{_mandir}/man5/gdeploy*

%changelog
* Tue Jan 10 2017 Sachidananda Urs <sac@redhat.com> 2.0.1-4
- Fix spec to address comment#19 from bug: 1344276

* Mon Nov 7 2016 Sachidananda Urs <sac@redhat.com> 2.0.1-3
- Fix spec file to conform to Fedora standards

* Wed Nov 2 2016 Sachidananda Urs <sac@redhat.com> 2.0.1-2
- Fixes bugs: 1390872, 1390871, 1387174

* Thu Sep 29 2016 Sachidananda Urs <sac@redhat.com> 2.0.1-1
- Removed ansible dependency from RHEL6

* Tue Aug 23 2016 Sachidananda Urs <sac@redhat.com> 2.0.1
- Add support for configuring NFS Ganesha, Samba, and CTDB

* Fri Jul 15 2016 Sachidananda Urs <sac@redhat.com> dev1
- NFS Ganesha related bug fixes.

* Wed Jun 8 2016 Sachidananda Urs <sac@redhat.com> master-2
- First release after master rebase

* Fri Jun 3 2016 Sachidananda Urs <sac@redhat.com> 2.0-16
- Cleaning up the spec file

* Mon Feb 1 2016 Sachidananda Urs <sac@redhat.com> 2.0
- New design, refer: doc/gdeploy-2

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
