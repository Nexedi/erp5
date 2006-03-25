Name:               CMFMailIn
Summary:            A Zope product to import emails into CMF sites.
Version:            1.0.0
Release:            4mdk
Group:              Development/Python
Requires:           zope CMF ZMailIn
License:            GPL
URL:                http://www.zope.org/Members/NIP/ZMailIn
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
CMFMailIn is a Zope product to import emails into CMF sites.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -q

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install www/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install tests/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/mailin
install skins/mailin/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/mailin


%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt LICENSE.txt VERSION.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.0.0-4mdk
- Make now signed rpm

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 1.0.0-3mdk
- Update spec in order to follows Mandrake Rules

* Wed May 21 2003 Sebastien Robin <jp@nexedi.com> 1.0.0-2nxd
- clean spec file

* Wed Mar 05 2003 Jean-Paul Smets <jp@nexedi.com> 1.0.0-1nxd
- Initial release
