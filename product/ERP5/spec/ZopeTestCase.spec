Name:               ZopeTestCase
Summary:            Unit test with Zope
Version:            0.9.0
Release:            1mdk
Group:              Development/Python
Requires:           zope
License:            ZPL
URL:                http://zope.org/Members/shh/ZopeTestCase
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
This products allows to implement unit test with Zope. This also
support functionnal testing.

http://zope.org/Members/shh/ZopeTestCase

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Testing/%{name}/
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Testing/%{name}/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Testing/%{name}/doc
install %{name}-%{version}/doc/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Testing/%{name}/doc
install %{name}-%{version}/doc/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Testing/%{name}/doc
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,zope,zope,0755)
%doc doc/VERSION.txt
%{_libdir}/zope/lib/python/Testing/%{name}/
#----------------------------------------------------------------------
%changelog
* Wed Aug 18 2004 Sebastien Robin <seb@nexedi.com> 0.9.0-1mdk
- Create the spec file
