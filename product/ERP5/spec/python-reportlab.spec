%{expand: %%define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%define pyname reportlab

Name:               python-reportlab
Summary:            Libraries to generate PDF for python
Version:            1.20
Release:            1mdk
Group:              Development/Python
Requires:           python
License:            BSD
URL:                http://www.reportlab.com
Packager:           Yoshinori Okuji <yo@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2
Patch1: python-reportlab-table.patch.bz2
Patch2: python-reportlab-image.patch.bz2
Patch3: python-reportlab-filename.patch.bz2

#----------------------------------------------------------------------
%description
The ReportLab Open Source PDF library is a proven industry-strength PDF
generating solution, that you can use for meeting your requirements and
deadlines in enterprise reporting systems.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -q 0
%patch1 -p1
%patch2 -p1
%patch3 -p1

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}
install *.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/colors
install demos/colors/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/colors
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/gadflypaper
install demos/gadflypaper/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/gadflypaper
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/odyssey
install demos/odyssey/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/odyssey
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/rlzope
install demos/rlzope/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/rlzope
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/stdfonts
install demos/stdfonts/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/stdfonts
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/tests
install demos/tests/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/demos/tests

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs
install docs/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/graphguide
install docs/graphguide/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/graphguide
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/images
install docs/images/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/images
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/reference
install docs/reference/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/reference
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/userguide
install docs/userguide/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/docs/userguide

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/extensions
install extensions/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/extensions

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/fonts
install fonts/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/fonts

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics
install graphics/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/charts
install graphics/charts/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/charts
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/widgets
install graphics/widgets/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/graphics/widgets

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/lib
install lib/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/lib

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfbase
install pdfbase/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfbase

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfgen
install pdfgen/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/pdfgen

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/platypus
install platypus/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/platypus

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/test
install test/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/test

install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools
install tools/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/docco
install tools/docco/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/docco
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/py2pdf
install tools/py2pdf/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/py2pdf
install -d $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/pythonpoint
install tools/pythonpoint/*.* $RPM_BUILD_ROOT%{_libdir}/python%{pyver}/%{pyname}/tools/pythonpoint

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README

%{_libdir}/python%{pyver}/%{pyname}/
#----------------------------------------------------------------------
%changelog
* Sun Apr 24 2005 Yoshinori Okuji <yo@nexedi.com> 1.20-1mdk
- Bump to 1.20.

* Mon Aug 16 2004 Yoshinori Okuji <yo@nexedi.com> 1.19-5mdk
- Import sys in pdfgen/pdfimages.py; it was just missing.

* Tue Jun  1 2004 Yoshinori Okuji <yo@nexedi.com> 1.19-4mdk
- Compress all patches.
- Fix the class Image so that it works with StringIO objects.

* Wed Apr 21 2004 Yoshinori Okuji <yo@nexedi.com> 1.19-3mdk
- Fix the install section of this spec.

* Wed Apr 21 2004 Yoshinori Okuji <yo@nexedi.com> 1.19-2mdk
- Fix a mysterios code in lib/utils.py, which deleted Image
  after importing it.

* Wed Apr 21 2004 Yoshinori Okuji <yo@nexedi.com> 1.19-1mdk
- New upstream version

* Thu Nov 20 2003 Sebastien Robin <seb@nexedi.com> 1.17-4mdk
- Added a new patch

* Wed Sep 12 2003 Sebastien Robin <seb@nexedi.com> 1.17-3mdk
- Make now signed rpm

* Thu Sep 04 2003 Sébastien Robin <seb@nexedi.com> 1.17-2mdk
- Update spec in order to follows Mandrake Rules

* Wed May 02 2003 Sebastien Robin <seb@nexedi.com> 1.17-1nxd
- Initial release
