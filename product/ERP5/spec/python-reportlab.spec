%{expand: %%define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%define pyname reportlab

Name:               python-reportlab
Summary:            Libraries to generate PDF for python
Version:            1.17
Release:            3mdk
Group:              Development/Python
Requires:           python
License:            GPL
URL:                http://www.reportlab.com
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
The ReportLab Open Source PDF library is a proven industry-strength PDF
generating solution, that you can use for meeting your requirements and
deadlines in enterprise reporting systems.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}
install %{name}-%{version}/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/colors
install %{name}-%{version}/demos/colors/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/colors
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/gadflypaper
install %{name}-%{version}/demos/gadflypaper/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/gadflypaper
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/odyssey
install %{name}-%{version}/demos/odyssey/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/odyssey
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/rlzope
install %{name}-%{version}/demos/rlzope/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/rlzope
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/stdfonts
install %{name}-%{version}/demos/stdfonts/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/stdfonts
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/tests
install %{name}-%{version}/demos/tests/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/tests

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs
install %{name}-%{version}/docs/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/graphguide
install %{name}-%{version}/docs/graphguide/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/graphguide
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/images
install %{name}-%{version}/docs/images/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/images
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/reference
install %{name}-%{version}/docs/reference/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/reference
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/userguide
install %{name}-%{version}/docs/userguide/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/userguide

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/extensions
install %{name}-%{version}/extensions/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/extensions

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/fonts
install %{name}-%{version}/fonts/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/fonts

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics
install %{name}-%{version}/graphics/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/charts
install %{name}-%{version}/graphics/charts/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/charts
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/widgets
install %{name}-%{version}/graphics/widgets/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/widgets

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/lib
install %{name}-%{version}/lib/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/lib

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfbase
install %{name}-%{version}/pdfbase/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfbase

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfgen
install %{name}-%{version}/pdfgen/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfgen

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/platypus
install %{name}-%{version}/platypus/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/platypus

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/test
install %{name}-%{version}/test/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/test

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools
install %{name}-%{version}/tools/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/docco
install %{name}-%{version}/tools/docco/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/docco
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/py2pdf
install %{name}-%{version}/tools/py2pdf/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/py2pdf
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/pythonpoint
install %{name}-%{version}/tools/pythonpoint/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/pythonpoint

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README

%{_libdir}/python%{pyver}/%{pyname}/
#----------------------------------------------------------------------
%changelog
* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.17-3mdk
- Make now signed rpm

* Thu Sep 04 2003 Sébastien Robin <seb@nexedi.com> 1.17-2mdk
- Update spec in order to follows Mandrake Rules

* Wed May 02 2003 Sebastien Robin <seb@nexedi.com> 1.17-1nxd
- Initial release
