# File: Base18-nxd.spec
#
# MMMShop
#
#   "MMMShop is a Zope framework which allows to implement online shops."
#

%define PRODUCT_DIRECTORY %{_libdir}/zope/lib/python/Products
%define ZOPE_INSTANCE_DIRECTORY /var/lib/zope

Name:               MMMShop
Summary:            A Zope CMF based online shop
Version:            0.5
Release:            4nxd
Group:              Development/Python
Requires:           zope CMF
License:            GPL
Vendor:             MMM
URL:                http://www.mmmanager.org/
Packager:           Jean-Paul Smets <jp@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir

Source0: http://www.mmmanager.org/Members/gitte/MMMShop-0.5.tar.bz2
Source1: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
MMMShop is a Zope CMF based online shop. It should be considered
as a generic framework to build an online shop on. The Storever
online shope (www.storever.com) was built on top of it.

http://www.mmmanager.org/

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
%setup -q

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT/%{PRODUCT_DIRECTORY}/%{name}
install %{name}/*.py $RPM_BUILD_ROOT/%{PRODUCT_DIRECTORY}/%{name}
install %{name}/*.txt $RPM_BUILD_ROOT/%{PRODUCT_DIRECTORY}/%{name}

install -d $RPM_BUILD_ROOT/%{PRODUCT_DIRECTORY}/%{name}/skins_nobabel
install %{name}/skins_nobabel/*.py $RPM_BUILD_ROOT/%{PRODUCT_DIRECTORY}/%{name}/skins_nobabel/
install %{name}/skins_nobabel/*.dtml $RPM_BUILD_ROOT/%{PRODUCT_DIRECTORY}/%{name}/skins_nobabel/

install -d $RPM_BUILD_ROOT/%{ZOPE_INSTANCE_DIRECTORY}/import
install import/*.zexp $RPM_BUILD_ROOT/%{ZOPE_INSTANCE_DIRECTORY}/import

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc INSTALL CHANGES DEPENDS

%{PRODUCT_DIRECTORY}/%{name}/*.py
%{PRODUCT_DIRECTORY}/%{name}/skins_nobabel/*.py
%{PRODUCT_DIRECTORY}/%{name}/skins_nobabel/*.dtml
%{ZOPE_INSTANCE_DIRECTORY}/import/*.zexp

#----------------------------------------------------------------------
%changelog
* Tue Jun 05 2003 Sebastien Robin <seb@nexedi.com> 0.1.0-4nxd
- Actually we need more than a patch since there's many new
  files, so we have to build a new archive

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-3nxd
- New patch

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-2nxd
- New patch

* Sun Dec 29 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-1nxd
- Initial release
