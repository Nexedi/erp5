Name:               ERP5Type
Summary:            Base objects for ERP5
Version:            0.9
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
ERP5Type contains most importants objects for ERP5. ERP5Type defines
most of methods that will be used by every object. It also implements
the Rapid Application Developpement feature used in ERP5.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%post
mkdir /var/lib/zope/Document

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Accessor
install %{name}-%{version}/Accessor/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Accessor
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install %{name}-%{version}/Constraint/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install %{name}-%{version}/Document/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install %{name}-%{version}/Interface/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install %{name}-%{version}/PropertySheet/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Tool
install %{name}-%{version}/Tool/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Tool
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
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

* Mon Feb 09 2004 Sebastien Robin <seb@nexedi.com> 0.1-4mdk
- Updated to the last code

* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.1-3mdk
- Changed permissions on files

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Mon May 12 2003 Sebastien Robin <seb@nexedi.com> 0.1-1nxd
- Create the spec file
