Name:               ZMailIn
Summary:            A Zope product to import emails into Zope sites.
Version:            1.0.1
Release:            3mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://www.zope.org/Members/NIP/ZMailIn
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
ZMailIn is a Zope product to import emails into Zope sites.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -q 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install www/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install dtml/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install help/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help/


%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc CREDITS.txt INSTALL.txt LICENSE.txt VERSION.txt CHANGES.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.0.1-3mdk
- Make now signed rpm

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 1.0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Wed Mar 05 2003 Jean-Paul Smets <jp@nexedi.com> 1.0.1-1nxd
- Initial release
