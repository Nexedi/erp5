%define name erp5diff
%define version 0.1
%define release 2nxd

Summary: XUpdate Generator for ERP5
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.bz2
License: GPL
Group: Development/Python
BuildRoot: %{_tmppath}/%{name}-buildroot
Url: http://erp5.org

%description
ERP5Diff is a XUpdate Generator for ERP5. It takes two XML files
as input data, and generates differences between these two XML
documents in XUpdate language.

ERP5Diff depends on more or less ERP5's XML data format. So this tool
cannot be used for general purpose, but might work if your XML files
are similar to ERP5's.

%prep
%setup -q

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files 
%defattr(-,root,root)
%doc PKG-INFO README
%{_libdir}/python*/site-packages/ERP5Diff*
%{_mandir}/man*/*
%attr(0755,root,root) %{_bindir}/%{name}

%changelog
* Wed Feb  4 2004 Sebastien Robin <seb@nexedi.com> 0.1-2nxd
- just added a return between each line

* Thu Dec  4 2003 Yoshinori Okuji <yo@nexedi.com> 0.1-1nxd
- initial package
