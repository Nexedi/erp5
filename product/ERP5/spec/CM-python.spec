# File: CM-python.spec
#
# CM-python
#
#   "CM-python allows to implement online payment with Zope"
#
# Installation requires:
#   cp libcm-mac.a %{_libdir}/
#   ln -s /usr/bin/python2.1 /usr/bin/python

Name:               CM-python
Summary:            A Zope product to build online computer shops
Version:            0.1
Release:            2nxd
Group:              Development/Python
Requires:           python
BuildRequires:      swig
License:            GPL
Vendor:             Nexedi
URL:                http://www.nexedi.org
Packager:           Jean-Paul Smets <jp@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir

Source0: http://www.nexedi.org/download/%{name}-%{version}.tar.bz2
Source1: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
StoreverShop is a Zope product to build online computer shops.

http://www.nexedi.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 1

#----------------------------------------------------------------------
%build
make clean
make all
make dist

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/python2.2/site-packages
install build/lib.linux-i686-2.1/cmmac.so $RPM_BUILD_ROOT%{_libdir}/python2.2/site-packages

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc MANIFEST cm-mac_wrap.doc payment.zexp CMMac.py

%{_libdir}/python2.2/site-packages/cmmac.so

#----------------------------------------------------------------------
%changelog
* Sun May 4 2003 Jean-Paul Smets <jp@nexedi.com> 0.1.0-2nxd
-- Upgrade to python2.2

* Sun Dec 29 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-1nxd
- Initial release
