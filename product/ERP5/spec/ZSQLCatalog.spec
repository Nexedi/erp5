%define product ZSQLCatalog
%define version 0.9.20060110
%define release 1

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   A Zope product to search the Zope database with SQL requests
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Requires:  zope-erp5

#----------------------------------------------------------------------
%description
ZSQLCatalog is a Zope product which allows to search the Zope database
with SQL requests. It replaces the standard Zope Catalog with a meta-catalog
which can be connected to any SQL relationnal database through ZSQLMethods.

#----------------------------------------------------------------------
%prep
%setup -c

%build


%install
%{__rm} -rf %{buildroot}
%{__mkdir_p} %{buildroot}/%{software_home}/Products
%{__cp} -a * %{buildroot}%{software_home}/Products/


%clean
%{__rm} -rf %{buildroot}

%post
mkdir /var/lib/zope/Extensions
ln -s %{software_home}/Products/%{name}/zsqlbrain.py /var/lib/zope/Extensions/
if [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%postun
if [ -f "%{_prefix}/bin/zopectl" ] && [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%files
%defattr(0644, root, root, 0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt
%{software_home}/Products/*

#----------------------------------------------------------------------
%changelog
* Tue Jan 10 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060110-1mdk
- New release for Mandriva 2006
- Spec file updated

* Tue Sep 01 2004 Sebastien Robin <seb@nexedi.com> 0.8-1mdk
- Final relase for Mandrake 10.1

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.2.1-9mdk
- Fix user permission

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.2.1-8mdk
- New Release For Mandkrake 10.1

* Tue Feb 17 2004 Sebatien Robin <seb@nexedi.com> 0.2.1-7mdk
- New release before Mandrake 10.0

* Mon Sep 08 2003 Sebatien Robin <seb@nexedi.com> 0.2.1-6mdk
- The content of this package was not updated because
  of a problem with the script which create the rpm

* Thu Sep 04 2003 Sebatien Robin <seb@nexedi.com> 0.2.1-5mdk
- change in the spec file '/usr/lib' by %%{_libdir}

* Thu Sep 04 2003 Sébastien Robin <seb@nexedi.com> 0.2.1-4mdk
- Update spec in order to follows Mandrake Rules

* Tue Jun 26 2003 Sébastien Robin <seb@nexedi.com> 0.2.1-3nxd
- Add the zsqlbrain in /var/lib/zope/Extensions

* Wed Apr 25 2003 Sébastien Robin <seb@nexedi.com> 0.2.1-2nxd
- Clean the spec file

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
