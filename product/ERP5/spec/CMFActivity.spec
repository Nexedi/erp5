Name:               CMFActivity
Summary:            Activity Tool for zope
Version:            0.1
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
This tools allows to implement activities for zope objects. 

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
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Activity
install %{name}-%{version}/Activity/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Activity
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/activity
install %{name}-%{version}/skins/activity/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/activity
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,zope,zope,0755)
%doc VERSION.txt
%{_libdir}/zope/lib/python/Products/%{name}/
#----------------------------------------------------------------------
%changelog
* Mon Feb 09 2004 Sebastien Robin <seb@nexedi.com> 0.1-1nxd
- Create the spec file
