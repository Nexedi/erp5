Name:               ERP5SyncML
Summary:            SyncML for ERP5
Version:            0.8
Release:            1mdk
Group:              Development/Python
Requires:           zope, ERP5Type, erp5diff
License:            GPL
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
To be written

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Conduit
install %{name}-%{version}/Conduit/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Conduit
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install %{name}-%{version}/Constraint/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install %{name}-%{version}/Document/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install %{name}-%{version}/Interface/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install %{name}-%{version}/PropertySheet/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install %{name}-%{version}/skins/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/redd
install %{name}-%{version}/skins/redd/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/redd
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,zope,zope,0755)
%doc VERSION.txt
%{_libdir}/zope/lib/python/Products/%{name}/
#----------------------------------------------------------------------
%changelog
* Tue Sep 01 2004 Sebastien Robin <seb@nexedi.com> 0.8-1mdk
- Final relase for Mandrake 10.1

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.1-5mdk
- New Release For Mandkrake 10.1

* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.1-3mdk
- Changed permissions on files

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Mon May 12 2003 Sebastien Robin <seb@nexedi.com> 0.1-1nxd
- Create the spec file
