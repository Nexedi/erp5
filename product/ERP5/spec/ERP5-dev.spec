Name:               ERP5-dev
Summary:            An installer of tools to developp ERP5
Version:            0.1
Release:            2nxd
Group:              Development/Python
Requires:           ERP5
License:            GPL
Vendor:             Nexedi
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir

Source0: http://www.erp5.org/download/%{name}-%{version}.tar.bz2
Source1: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
ERP5-dev install all packages needed in order to get a developpment
box for erp5.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 1

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT/usr/bin/
install %{name}-%{version}/install_erp5_dev $RPM_BUILD_ROOT/usr/bin/
install -d $RPM_BUILD_ROOT/var/lib/zope/Products
install %{name}-%{version}/update_cvs $RPM_BUILD_ROOT/var/lib/zope/Products/
install -d $RPM_BUILD_ROOT/var/lib/zope/import
install %{name}-%{version}/publish_nexedi.zexp $RPM_BUILD_ROOT/var/lib/zope/import/
install -d $RPM_BUILD_ROOT/var/lib/zope
install %{name}-%{version}/vhost_append $RPM_BUILD_ROOT/var/lib/zope/
%clean
rm -rf $RPM_BUILD_ROOT


#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
#%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt
/usr/bin
/var/lib/zope

#----------------------------------------------------------------------
%changelog
* Mon Jul 21 2003 Sebastien Robin <seb@nexedi.com> 0.1.0-1nxd
- Modified the Vhost config of apache so that we don't have
errors of catalog anymore.
* Mon Jul 15 2003 Sebastien Robin <seb@nexedi.com> 0.1.0-1nxd
- The previous rpm destroyed the tmp directory
* Wed Jun 25 2003 Sebastien Robin <seb@nexedi.com> 0.1.0-1nxd
- Initial release
