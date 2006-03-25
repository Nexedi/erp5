# File: ZSQLCatalog-nxd.spec
#
# ZSQLCatalog
#
#   "ZSQLCatalog is a Zope product to search the Zope database with SQL requests"
#

%define PRODUCT_DIRECTORY /var/lib/zope/Products
%define USER  jp

Name:               ZSQLCatalog
Summary:            A Zope product to search the Zope database with SQL requests
Version:            0.2.1
Release:            1nxd
Group:              Development/Python
Requires:           Zope
Copyright:          GPL
Vendor:             Nexedi
URL:                http://www.erp5.org
Packager:           Jean-Paul Smets <jp@nexedi.com>
BuildRoot:          /var/tmp/%{name}-%{version}-rootdir

Source0: http://www.erp5.org/download/%{name}-%{version}.tar.bz2
Source1: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
ZSQLCatalog is a Zope product which allows to search the Zope database
with SQL requests. It replaces the standard Zope Catalog with a meta-catalog
which can be connected to any SQL relationnal database through ZSQLMethods.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

# Create the source code from the local Zope
rm -rf /home/%{USER}/rpm/BUILD/%{name}-%{version}
cp -ur %{PRODUCT_DIRECTORY}/%{name} /home/%{USER}/rpm/BUILD/%{name}-%{version}
cd /home/%{USER}/rpm/BUILD/
tar cjf /home/%{USER}/rpm/SOURCES/%{name}-%{version}.tar.bz2 %{name}-%{version}
rm -rf /home/%{USER}/rpm/BUILD/%{name}-%{version}

rm -rf $RPM_BUILD_ROOT
%setup -a 1

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.py $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/www
install %{name}-%{version}/www/*.gif $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/www

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/tests

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/dtml

install -d $RPM_BUILD_ROOT/usr/lib/zope/Extensions
install %{name}-%{version}/zsqlbrain.py $RPM_BUILD_ROOT/usr/lib/zope/Extensions

%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt

/usr/lib/zope/lib/python/Products/%{name}/*.py
/usr/lib/zope/lib/python/Products/%{name}/*.txt
/usr/lib/zope/lib/python/Products/%{name}/help/*.stx
/usr/lib/zope/lib/python/Products/%{name}/www/*.gif
/usr/lib/zope/lib/python/Products/%{name}/tests/*.py
/usr/lib/zope/lib/python/Products/%{name}/dtml/*.dtml
/usr/lib/zope/Extensions/zsqlbrain.py

#----------------------------------------------------------------------
%changelog
* Wed Apr 9 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.1-1nxd
- Updated source

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-5nxd
- Added brain

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.2.0-4nxd
- Code update

* Thu Dec 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.2.0-2nxd
- Initial release

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.1.0-1nxd
- Initial release
