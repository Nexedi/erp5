Name:               python-reportlab-accel
Summary:            Accelerator for the ReportLab Toolkit
Version:            0.52.20050424
Release:            1mdk
Group:              Development/Python
Requires:           python
BuildRequires:      python-devel
License:            GPL
URL:                http://www.reportlab.com
Packager:           Yoshinori Okuji <yo@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
A C coded extension accelerator for the ReportLab Toolkit.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -q 0

#----------------------------------------------------------------------
%build
python setup.py build

#----------------------------------------------------------------------
%install
python setup.py install --root=%{buildroot}

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.extensions

%{_libdir}/python*.*/site-packages/*.so

#----------------------------------------------------------------------
%changelog
* Sun Apr 24 2005 Yoshinori Okuji <yo@nexedi.com> 0.52.20050424-1mdk
- Initial release
