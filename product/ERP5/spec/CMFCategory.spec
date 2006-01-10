Name:               CMFCategory
Summary:            All algorithms related to categories and relations in CMF
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
Category objects allow to define classification categories
in an ERP5 portal. For example, a document may be assigned a color
attribute (red, blue, green). Rather than assigning an attribute
with a pop-up menu (which is still a possibility), we can prefer
in certain cases to associate to the object a category. In this
example, the category will be named color/red, color/blue or color/green


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
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install %{name}-%{version}/Constraint/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install %{name}-%{version}/Document/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install %{name}-%{version}/Interface/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install %{name}-%{version}/PropertySheet/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc
install %{name}-%{version}/doc/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install %{name}-%{version}/www/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
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

* Mon Jun 14 2004 Sebastien Robin <seb@nexedi.com> 0.1-5mdk
- New release for Mandrake 10.1

* Tue Feb 17 2004 Sebastien Robin <seb@nexedi.com> 0.1-4mdk
- New release before mandrake 10

* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.1-3mdk
- Changed permissions on files

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Mon May 12 2003 Sebastien Robin <seb@nexedi.com> 0.1-1nxd
- Create the spec file
