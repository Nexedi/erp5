# File: Base18-nxd.spec
#
# StoreverShop
#
#   "StoreverShop is a Zope CMF Product to implement a computer shop"
#

%define SOURCE_PRODUCT_DIRECTORY /var/lib/zope/Products
%define USER  jp
%define PRODUCT_DIRECTORY %{_libdir}/zope/lib/python/Products
%define ZOPE_INSTANCE_DIRECTORY /var/lib/zope

Name:               StoreverShop
Summary:            A Zope product to build online computer shops
Version:            0.1.0
Release:            7nxd
Group:              Development/Python
Requires:           zope Localizer
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

#Create the source code from the local Zope
rm -rf /home/%{USER}/rpm/BUILD/%{name}-%{version}
cp -ur %{SOURCE_PRODUCT_DIRECTORY}/%{name} /home/%{USER}/rpm/BUILD/%{name}-%{version}
cd /home/%{USER}/rpm/BUILD/
tar cjf /home/%{USER}/rpm/SOURCES/%{name}-%{version}.tar.bz2 %{name}-%{version}
rm -rf /home/%{USER}/rpm/BUILD/%{name}-%{version}

rm -rf $RPM_BUILD_ROOT
mkdir $RPM_BUILD_ROOT
%setup -q

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}
install *.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/storever
install skins/storever/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/storever
install skins/storever/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/storever
install skins/storever/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/storever
install skins/storever/*.ico $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/storever

install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/cm_storever
install skins/cm_storever/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/cm_storever

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt

%{PRODUCT_DIRECTORY}/%{name}/*.py
%{PRODUCT_DIRECTORY}/%{name}/*.txt
%{PRODUCT_DIRECTORY}/%{name}/skins/storever/*.py
%{PRODUCT_DIRECTORY}/%{name}/skins/storever/*.dtml
%{PRODUCT_DIRECTORY}/%{name}/skins/storever/*.ico
%{PRODUCT_DIRECTORY}/%{name}/skins/storever/*.png
%{PRODUCT_DIRECTORY}/%{name}/skins/cm_storever/*.dtml

#----------------------------------------------------------------------
%changelog
* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-7nxd
- Extended skin

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-6nxd
- fixed texte-libre in cm

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-5nxd
- .ico file

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-4nxd
- logo.png

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-3nxd
- Fixed skin for cm

* Mon Dec 30 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-2nxd
- Added skin for cm

* Sun Dec 29 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-1nxd
- Initial release
