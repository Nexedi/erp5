%define name FunctionalTests
%define version 0.4
%define release 1nxd

Summary: Functional Testing module for Zope
Name: %{name}
Version: %{version}
Release: %{release}
License: ZPL
URL: http://www.zope.org/Members/tseaver/FunctionalTests
Group: Development/Python
Source0: FunctionalTests-%{version}.tar.bz2
Patch1: FunctionalTests-0.4-python-path.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
Requires: python >= 2.1

%description
FunctionalTests is an automated framework for recording and replaying
"functional" tests of a Zope web application. Requests can be either
HTTP requests, including authentication, cookies, and form variables,
or ZEO-based Python functions (especially useful for
setup/teardown/postcondition implementations).

%prep
%setup -q
%patch1 -p1

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root)
%doc doc/* examples
%{_libdir}/python*/site-packages/*
%{_bindir}/ft*

%changelog
* Mon Nov 17 2003 Yoshinori OKUJI <yo@nexedi.com> 0.4-1nxd
- initial version
