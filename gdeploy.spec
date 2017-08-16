%global gdeploymod ansible/modules/gdeploy
%global gdeploytemp %{_datadir}/gdeploy

Name:           gdeploy
Version:        2.0.2
Release:        13
Summary:        Tool to deploy and manage GlusterFS cluster

License:        GPLv3+
URL:            https://github.com/gluster/gdeploy
Source0:        %{url}/archive/v%{version}-%{release}.tar.gz#/%{name}-%{version}-%{release}.tar.gz
BuildArch:      noarch
Requires:       PyYAML
Requires:       ansible > 2.3
Requires:       python2
Requires:       lvm2

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
%setup -q -n %{name}-%{version}-%{release}

# We are sticking to python2 till we clean up the code
# * Change print statements
# * Change xrange function usage
# * Change the except syntax
# ...

%build
%py2_build
pushd docs
make html
popd

%install
# Install the binary and python libraries
%py2_install

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

# Install the gdeploy plugin
mkdir -p %{buildroot}/%{python2_sitelib}/ansible/plugins/callback
install -p -m 755 plugins/callback/gdeploy.py \
        %{buildroot}/%{python2_sitelib}/ansible/plugins/callback/

# Documentation
mkdir -p %{buildroot}/%{_pkgdocdir}
cp -rp docs/build/html examples %{buildroot}/%{_pkgdocdir}

# Man pages
mkdir -p %{buildroot}/%{_mandir}/man1/ \
       %{buildroot}/%{_mandir}/man5/
cp -p man/gdeploy.1* %{buildroot}/%{_mandir}/man1/
cp -p man/gdeploy.conf* %{buildroot}/%{_mandir}/man5/

%files
%{_bindir}/gdeploy
%{python2_sitelib}/gdeploy*
%{gdeploytemp}
%{python2_sitelib}/%{gdeploymod}
%{_bindir}/gluster-replace-node
%{python2_sitelib}/ansible/plugins/callback/gdeploy.py*

%doc README.md TODO
%license LICENSE
%{_mandir}/man1/gdeploy*
%{_mandir}/man5/gdeploy*

%package doc
Summary: gdeploy documentation
BuildRequires:  python2-sphinx

%description doc
gdeploy is an Ansible based deployment tool, used to deploy and configure
GlusteFS.

gdeploy-doc package provides the documentation for writing gdeploy
configuration files to deploy and configure GlusterFS.

%files doc
%doc %{_pkgdocdir}

%changelog
* Wed Aug 9 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-13
- Fix spec to address comment#28 from bug: 1344276

* Tue Jun 27 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-12
- Do not throw `volume start failed' error if volume is already started
- Add service `glusterfssharedstorage' to NFS Ganesha pre-requisites
- Add service `nfs-ganesha' to NFS Ganesha pre-requisites

* Thu Jun 22 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-11
- Updated extras/scripts to enable multipath

* Thu May 18 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-10
- Use shell module instead of script while executing a script

* Tue May 16 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-9
- Print the status of add-node command

* Mon May 15 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-8
- Do not export a volume unless specified in [nfs-ganesha] section

* Thu May 11 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-7
- Move the modues to ansible/modules from ansible/modules/extras

* Fri May 5 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-6
- Fixes a traceback caused for accessing non-existent key

* Fri May 5 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-5
- Fixes bugs: 1447271 1446509 1446092 1444829

* Tue Apr 25 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-4
- Add cachesize variable to [backend-setup] section

* Thu Apr 13 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-3
- Fix a traceback in RHEL6, catch exception and print message

* Thu Mar 30 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-2
- Fixed an issue where playbooks were installed wrongly

* Wed Mar 22 2017 Sachidananda Urs <sac@redhat.com> 2.0.2-1
- Fixes NFS Ganesha delete node issue
- Add support for RAID5

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
