Name:               CMFReportTool
Summary:            A Zope product to generate PDF reports
Version:            0.1.1
Release:            5mdk
Group:              Development/Python
Requires:           zope CMF python-reportlab
License:            GPL
URL:                http://www.zope.org/Members/jack-e/CMFReportTool/
Packager:           Sebastien Robin <seb@nexedi.com>
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

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc
install doc/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/examples
install doc/examples/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/examples
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/htmldoc
install doc/htmldoc/*.* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/doc/htmldoc

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
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-5md
- Make now signed rpm

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-4mdk
- Update spec in order to follows Mandrake Rules

* Wed May 02 2003 Sebastien Robin <seb@nexedi.com> 0.1.1-3nxd
- Change dependency Reportlab to python-reportlab

* Wed Mar 05 2003 Jean-Paul Smets <jp@nexedi.com> 0.1.1-2nxd
- Added help directory

* Wed Mar 05 2003 Jean-Paul Smets <jp@nexedi.com> 0.1.1-1nxd
- Initial release
