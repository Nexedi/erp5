Name:               ZSQLCatalog
Summary:            A Zope product to search the Zope database with SQL requests
Version:            0.8
Release:            1mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
ZSQLCatalog is a Zope product which allows to search the Zope database
with SQL requests. It replaces the standard Zope Catalog with a meta-catalog
which can be connected to any SQL relationnal database through ZSQLMethods.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%post
mkdir /var/lib/zope/Extensions
cp %{_libdir}/zope/lib/python/Products/%{name}/zsqlbrain.py /var/lib/zope/Extensions/


#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/spec
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install %{name}-%{version}/www/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,zope,zope,0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt
%{_libdir}/zope/lib/python/Products/%{name}/
#----------------------------------------------------------------------
%changelog
* Tue Sep 01 2004 Sebastien Robin <seb@nexedi.com> 0.8-1mdk
- Final relase for Mandrake 10.1

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.2.1-9mdk
- Fix user permission

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.2.1-8mdk
- New Release For Mandkrake 10.1

* Tue Feb 17 2004 Sebatien Robin <seb@nexedi.com> 0.2.1-7mdk
- New release before Mandrake 10.0

* Mon Sep 08 2003 Sebatien Robin <seb@nexedi.com> 0.2.1-6mdk
- The content of this package was not updated because
  of a problem with the script which create the rpm

* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 0.2.1-5mdk
- change in the spec file '/usr/lib' by %{_libdir}

* Thu Sep 04 2003 Sébastien Robin <seb@nexedi.com> 0.2.1-4mdk
- Update spec in order to follows Mandrake Rules

* Tue Jun 26 2003 Sébastien Robin <seb@nexedi.com> 0.2.1-3nxd
- Add the zsqlbrain in /var/lib/zope/Extensions

* Wed Apr 25 2003 Sébastien Robin <seb@nexedi.com> 0.2.1-2nxd
- Clean the spec file

* Wed Apr 9 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.1-1nxd
- Updated source

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-5nxd
- Added brain

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-4nxd
- Code update

* Thu Dec 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.2.0-2nxd
- Initial release

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-1nxd
- Initial release
