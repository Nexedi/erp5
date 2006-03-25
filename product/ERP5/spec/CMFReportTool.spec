Name:               CMFReportTool
Summary:            A Zope product to generate PDF reports
Version:            0.1.1.20050422
Release:            1mdk
Group:              Development/Python
Requires:           zope CMF python-reportlab
License:            GPL
URL:                http://www.zope.org/Members/jack-e/CMFReportTool/
Packager:           Yoshinori Okuji <yo@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
CMFReportTool is a Zope which extends the Zope CMF
to implement PDF skins. PDF skins allow to generate reports
which are automatically converted into PDF files with
the python reportlab library.

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
install oo2pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc
install doc/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/examples
install doc/examples/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/examples
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/diagram
install doc/diagram/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/diagram
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/pdf
install doc/pdf/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/pdf
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/pml
install doc/pml/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/pml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install dtml/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install help/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install Extensions/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/RenderPDF
install RenderPDF/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/RenderPDF

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/zpt_reporttool
install skins/zpt_reporttool/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/zpt_reporttool


%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt TODO.txt LICENSE.txt COPYRIGHT.txt

%{_libdir}/zope/lib/python/Products/%{name}/

#----------------------------------------------------------------------
%changelog
* Thu Apr  4 2005 Yoshinori Okuji <yo@nexedi.com> 0.1.1.20050422-1mdk
- Grab a new upstream version.

* Wed May 19 2004 Yoshinori Okuji <yo@nexedi.com> 0.1.1-7.20040421.3mdk
- Correct the return value of wrap in case where the paragraph cannot
  be split.

* Wed Apr 28 2004 Yoshinori Okuji <yo@nexedi.com> 0.1.1-7.20040421.2mdk
- Compress the patch with bzip2
- Add one more patch to fix a unicode problem in td.

* Wed Apr 21 2004 Yoshinori Okuji <yo@nexedi.com> 0.1.1-7.20040421.1mdk
- Upgrade to the current CVS version

* Thu Nov 20 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-6mdk
- Added new patch

* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-5mdk
- Make now signed rpm

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-4mdk
- Update spec in order to follows Mandrake Rules

* Wed May 02 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-3nxd
- Change dependency Reportlab to python-reportlab

* Wed Mar 05 2003 Jean-Paul Smets <jp@nexedi.com> 0.1.1-2nxd
- Added help directory

* Wed Mar 05 2003 Jean-Paul Smets <jp@nexedi.com> 0.1.1-1nxd
- Initial release
