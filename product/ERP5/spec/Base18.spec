Name:               Base18
Summary:            Base18 is a Zope product to implement multilingual portals
Version:            0.2.0
Release:            13mdk
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
Base18 is a Zope product to implement multilingual portals
It extends the Zope CMF by allowing documents to be split into
a list of paragraphs which can be translated through a message catalog.

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
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/default_wiki_content
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install %{name}-%{version}/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/interfaces
install %{name}-%{version}/interfaces/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/interfaces
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/content18
install %{name}-%{version}/skins/content18/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/content18
install %{name}-%{version}/skins/content18/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/content18
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.props $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/nexedi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/zpt_content18
install %{name}-%{version}/skins/zpt_content18/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/zpt_content18
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/zpt_nexedi
install %{name}-%{version}/skins/zpt_nexedi/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/zpt_nexedi
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/spec
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt
%{_libdir}/zope/lib/python/Products/%{name}/
#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 0.2.0.13mdk
- Make now signed rpm

* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 0.2.0-12mdk
- change in the spec file '/usr/lib' by %{_libdir}

* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 0.2.0-11mdk
- Update this rpm in order to follows Mandrake rules

* Thu May 30 2003 Sebastien Robin <seb@nexedi.com> 0.2.0-10nxd
- Update the changelog, there were bad version numbers

* Thu Jan 30 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-9nxd
- Missing interfaces

* Thu Jan 30 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-9nxd
- Missing interfaces

* Tue Jan 21 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-8nxd
- Missing menu_box

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-7nxd
- Fixed again missing skins

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-6nxd
- Fixed again missing skins

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-5nxd
- Code update for latest CMF - recover from crash

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.2.0-1nxd
- Initial release
