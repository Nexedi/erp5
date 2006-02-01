%define product ERP5
%define version 0.11
%define release 5

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   A Zope framework to implement ERP software
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Conflicts: ERP5
Requires:  erp5-zope >= 2.7.8, erp5-CMFPhoto, erp5-Formulator, zope-CMFReportTool, zope-Localizer, zope-Photo, zope-ZMySQLDA, zope-BTreeFolder2, zope-CMFMailIn, zope-ERP5Catalog, zope-ERP5Form, zope-ERP5SyncML, zope-CMFCategory, zope-ERP5Type, python-numeric, python-psyco, python-glpk, zope-CMFActivity, zope-ERP5Security, zope-ERP5OOo, zope-ExtFile, zope-TimerService

#----------------------------------------------------------------------
%description
ERP5 is a Zope framework which allows to implement ERP software.
It includes a Rapid Application Development system and a Universal
Business Model which together allow to model any business process in
very short time.

#----------------------------------------------------------------------
%prep
%setup -c

%build


%install
%{__rm} -rf %{buildroot}
%{__mkdir_p} %{buildroot}/%{software_home}/Products
%{__cp} -a * %{buildroot}%{software_home}/Products/
cat > README.urpmi <<EOF

ERP5 need a MySQL-Max version 5.x.x server to work properly. Because this server
can be installed on another machine, we let you the choice to install it or not.

If you want to let ERP5 working on a standalone machine, please install MySQL-Max
package and its dependancies.

EOF

%clean
%{__rm} -rf %{buildroot}

%post
mkdir /var/lib/zope/Extensions
mkdir /var/lib/zope/PropertySheet
mkdir /var/lib/zope/Constraint
mkdir /var/lib/zope/bt5
chmod -R 755 /var/lib/zope
chown -R zope:zope /var/lib/zope
ln -s %{software_home}/Products/%{product}/Extensions/zsqlbrain.py /var/lib/zope/Extensions/
ln -s %{software_home}/Products/%{product}/Extensions/InventoryBrain.py /var/lib/zope/Extensions/
mv %{software_home}/Products/%{product}/utils/cvs_update.sh /var/lib/zope/Products/
if [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%postun
if [ -f "%{_prefix}/bin/zopectl" ] && [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%files
%defattr(0644, zope, zope, 0755)
%doc %{product}/VERSION.txt %{product}/README.txt %{product}/INSTALL.txt %{product}/CREDITS.txt  %{product}/GPL.txt %{product}/ZPL.txt README.urpmi
%{software_home}/Products/*

#----------------------------------------------------------------------
%changelog
* Mon Jan 30 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-5mdk
- Correct /var/lib/zope/ ownership and rights

* Mon Jan 30 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-4mdk
- Add missing symlink to InventoryBrain.py

* Mon Jan 30 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-3mdk
- New build from the CVS

* Fri Jan 27 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-2mdk
- New build from the CVS
- Create a bt5 folder in /var/lib/zope

* Thu Jan 26 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-1mdk
- Update to version 0.11
- Put the cvs_update script in the right place

* Wed Jan 25 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-9mdk
- Add README.urpmi in %%doc

* Mon Jan 23 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-8mdk
- Add a README to warn user that ERP5 need a MySQL-Max server to work
- Delete "Requires: MySQL-Max >= 5" statement

* Mon Jan 23 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-7mdk
- ERP5 Zope product also need Timer Service to make Portal Alarm Working

* Mon Jan 23 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-6mdk
- Fix bad symlink

* Thu Jan 19 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-5mdk
- Don't need Translation Service Zope product for ERP5

* Thu Jan 19 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-4mdk
- Add missing custom post-command

* Wed Jan 18 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-3mdk
- Add a version to the required zope package

* Wed Jan 18 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-2mdk
- Add ExtFile Zope Product as required

* Wed Jan 18 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-1mdk
- Update to version 0.10

* Mon Jan 16 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060116-1mdk
- New build from the CVS

* Tue Jan 10 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060110-1mdk
- New release for Mandriva 2006
- Spec file updated

* Tue Sep 01 2004 Sebastien Robin <seb@nexedi.com> 0.8-1mdk
- New release for Mandrake 10.1

* Tue Jun 15 2004 Sebastien Robin <seb@nexedi.com> 0.1-26mdk
- Fix some sql queries

* Thu Jun 10 2004 Sebastien Robin <seb@nexedi.com> 0.1-25mdk
- New release for Mandrake 10.1

* Mon Nov 03 2003 Sebastien Robin <seb@nexedi.com> 0.1-24mdk
- Added dependencies to python-numeric and gplk

* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.1-23mdk
- Changed permissions on files

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1-22mdk
- Update spec in order to follows Mandrake Rules

* Wed May 21 2003 Sébastien Robin <seb@nexedi.com> 0.1-21nxd
- Added dependencies : python-imaging TranslationService

* Tue May 13 2003 Sébastien Robin <seb@nexedi.com> 0.1-20nxd
- Added dependencies : ERP5Catalog, ERP5Form, CMFCategory, ERP5SyncML...
- We need theses dependencies because ERP5 was splitted in several products

* Wed May 02 2003 Sébastien Robin <seb@nexedi.com> 0.1-19nxd
- Added dependencies : PyXML, python-reportlab
- Remove dependencies : python2.1-xml

* Mon Apr 28 2003 Sébastien Robin <seb@nexedi.com> 0.1-17nxd
- Added a dependency (ZMySQLDA), since ERP5 is only tested
  with mysql actually. May be it should be removed afterwards.

* Wed Apr 25 2003 Sébastien Robin <seb@nexedi.com> 0.1-16nxd
- Clean this spec file in order to not copy local files
- Remove dependencies (zope-zserver)
- Add the directory Constraint

* Wed Mar 5 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-15nxd
- Added missing dependencies (zope-zserver)

* Wed Mar 5 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-14nxd
- Added missing dependencies (CMFReport CMFMailIn)

* Wed Mar 5 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-13nxd
- Added missing dependencies (Base18)

* Tue Feb 25 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-12nxd
- Added props

* Tue Feb 25 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-11nxd
- Added images

* Tue Feb 25 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-10nxd
- Code update

* Thu Feb 13 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-9nxd
- Code update

* Mon Feb 2 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-8nxd
- Added portal.gif

* Mon Feb 2 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-7nxd
- Added Core

* Mon Feb 2 2003 Jean-Paul Smets <jp@nexedi.com> 0.1-6nxd
- Code update + do it again

* Thu Dec 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.1-2nxd
- CVS Updates

* Mon Nov 4 2002 Jean-Paul Smets <jp@nexedi.com> 0.1-1nxd
- Initial release
