Name:               Localizer
Summary:            A Zope product to localize applications
Version:            1.0.1
Release:            3mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://www.j-david.net/software/localizer/
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
Localizer is a Zope product which allows to implement localization
services based on gettext.

A complete guide is available online at
http://www.j-david.net/software/localizer/guide/index_html

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.en $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.es $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.fr $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/img
install %{name}-%{version}/img/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/img

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/locale
install %{name}-%{version}/locale/*.mo $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/locale
install %{name}-%{version}/locale/*.po $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/locale
install %{name}-%{version}/locale/*.pot $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/locale

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/ui
install %{name}-%{version}/ui/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/ui

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt TODO.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 1.0.1-3mdk
- change in the spec file '/usr/lib' by %{_libdir}

* Wed Sep 3 2003 Sebastien Robin <sebnexedi.com> 1.0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com> 1.0.1-1nxd
- Update to version 1.0.1

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.8.1-1nxd
- Initial release
