Name:               ZMySQLDA
Summary:            A Zope connector to Mysql
Version:            2.0.9b2
Release:            4mdk
Group:              Development/Python
Requires:           zope MySQL-python
License:            GPL
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch


Source: %{name}-%{version}.tar.bz2
Patch1: ZMySQLDA-2.0.9b2_with_MySQL-python-0.9.0.patch
Patch2: ZMySQLDA-2.0.9b2_release-unlocked-lock.patch

#----------------------------------------------------------------------
%description
ZMySQLDA allows to quickly connect to Mysql with Zope.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
%setup -a 0
%patch1 -p1
%patch2 -p1

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install help/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/icons
install icons/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/icons

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc CHANGES.txt DEPENDENCIES.txt README.txt VERSION.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 2.0.9b2-4mdk
- Make now signed rpm

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 2.0.9b2-3mdk
- Change in the requires field "Zope" by "zope"

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 2.0.9b2-2mdk
- Update spec in order to follows Mandrake Rules

* Mon Apr 28 2003 Sebastien Robin <seb@nexedi.com> 2.0.9b2-1nxd
- It was first made by converting a Debian Package. But since
we need to modify it, we needed to build by the rpm way.

* Wed Mar 23 2003 Sebastien Robin <seb@nexedi.com> 2.0.8-2nxd
- It was first made by converting a Debian Package. But since
we need to modify it, we needed to build by the rpm way.
