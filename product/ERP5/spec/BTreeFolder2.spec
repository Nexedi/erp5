Name:               BTreeFolder2
Summary:            A Zope product to implement large size folders
Version:            0.5.0
Release:            7mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://www.zope.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
BTreeFolder2 is a Zope product to implement large size folders.

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
install %{name}-%{version}/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt CREDITS.txt LICENSE.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 0.5.0-7mdk
- Make now signed rpm

* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 0.5.0-6mdk
- change in the spec file '/usr/lib' by %{_libdir}

* Thu Sep 04 2003 Sebastien Robin <seb@nexedi.com> 0.5.0-5mdk
- Update spec in order to follows Mandrake Rules

* Mon Apr 28 2003 Sebastien Robin <seb@nexedi.com> 0.5.0-4nxd
- dtml files where not installed
- clean the spec file

* Mon Nov 4 2002 Jean-Paul Smets <jp@nexedi.com> 0.5.0-1nxd
- Initial release
