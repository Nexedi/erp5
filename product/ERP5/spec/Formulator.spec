Name:               Formulator
Summary:            Allows to quickly implements forms with Zope
Version:            1.6.1
Release:            1mdk
Group:              Development/Python
Requires:           zope
License:            GPL
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2
Patch1: Formulator-1.6.1-editable.patch

#----------------------------------------------------------------------
%description
Formulator allows to quickly implement forms with Zope.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -b 0
%patch1 -p1

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install help/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install help/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install tests/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install www/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt CREDITS.txt LICENSE.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.4.2-1mdk
- Updated to version 1.6.1
- added a small patch in order to allow to display field
- read only

* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.4.2-1mdk
- Updated to version 1.4.2

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-9mdk
- Remove old variables 'ZOPE_NAME' and replace it with 'name'

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-8mdk
- Update spec in order to follows Mandrake Rules

* Thu Jul 24 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-7nxd
- New patch made by me in order allow float with commas

* Wed Jun 11 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-6nxd
- New patch made by me in order to get an xml ordered

* Thu Jun 3 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-5nxd
- New patch again in order to apply a script on a line of a listbox (with the cell value)

* Thu Jun 3 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-4nxd
- New patch in order to apply a script on a line of a listbox (with the cell value)

* Tue May 13 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-3nxd
- New patch in order to improve Formulator with XML

* Wed Mar 26 2003 Sebastien Robin <seb@nexedi.com> 1.3.1-1nxd
- Update to release 1.3.1 of the formulator
- Added patch made by Jean-Paul Smets <jp@nexedi.com> wich allows
to use a list of keys.

* Mon Nov 4 2002 Sebastien Robin <seb@nexedi.com> 1.2.0-2nxd
- Added patch in order to dynamically change the name

* Mon Nov 4 2002 Jean-Paul Smets <jp@nexedi.com> 1.2.0-1nxd
- Initial release
