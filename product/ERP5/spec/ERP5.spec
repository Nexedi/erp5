Name:               ERP5
Summary:            A Zope framework to implement ERP software
Version:            0.8
Release:            1mdk
Group:              Development/Python
Requires:           zope ExtFile ZSQLCatalog Photo CMFPhoto BTreeFolder2 Formulator Localizer CMFReportTool CMFMailIn ZMySQLDA PyXML python-reportlab ERP5Catalog ERP5Form ERP5SyncML CMFCategory ERP5Type python-imaging TranslationService, python-numeric, python-psyco, python-glpk, CMFActivity
License:            GPL
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
ERP5 is a Zope framework which allows to implement ERP software.
It includes a Rapid Application Development system and a Universal
Business Model which together allow to model any business process in
very short time.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%post
mkdir /var/lib/zope/Extensions
cp %{_libdir}/zope/lib/python/Products/%{name}/Extensions/InventoryBrain.py /var/lib/zope/Extensions/


#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Capacity
install %{name}-%{version}/Capacity/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Capacity
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install %{name}-%{version}/Constraint/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Core
install %{name}-%{version}/Core/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Core
install %{name}-%{version}/Core/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Core
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/DeliverySolver
install %{name}-%{version}/DeliverySolver/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/DeliverySolver
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install %{name}-%{version}/Document/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install %{name}-%{version}/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/functest
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/functest/anonymous
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/functest/member
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/import
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install %{name}-%{version}/Interface/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/patch
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install %{name}-%{version}/PropertySheet/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install %{name}-%{version}/PropertySheet/*.stx $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Simulation
install %{name}-%{version}/Simulation/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Simulation
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5
install %{name}-%{version}/skins/erp5/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5
install %{name}-%{version}/skins/erp5/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5
install %{name}-%{version}/skins/erp5/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5
install %{name}-%{version}/skins/erp5/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5
install %{name}-%{version}/skins/erp5/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_accounting
install %{name}-%{version}/skins/erp5_accounting/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_accounting
install %{name}-%{version}/skins/erp5_accounting/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_accounting
install %{name}-%{version}/skins/erp5_accounting/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_accounting
install %{name}-%{version}/skins/erp5_accounting/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_accounting
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_crm
install %{name}-%{version}/skins/erp5_crm/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_crm
install %{name}-%{version}/skins/erp5_crm/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_crm
install %{name}-%{version}/skins/erp5_crm/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_crm
install %{name}-%{version}/skins/erp5_crm/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_crm
install %{name}-%{version}/skins/erp5_crm/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_crm
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_generator
install %{name}-%{version}/skins/erp5_generator/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_generator
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_test
install %{name}-%{version}/skins/erp5_test/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_test
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_tmp
install %{name}-%{version}/skins/erp5_tmp/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_tmp
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_trade
install %{name}-%{version}/skins/erp5_trade/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_trade
install %{name}-%{version}/skins/erp5_trade/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_trade
install %{name}-%{version}/skins/erp5_trade/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_trade
install %{name}-%{version}/skins/erp5_trade/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/erp5_trade
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/pro
install %{name}-%{version}/skins/pro/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/pro
install %{name}-%{version}/skins/pro/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/pro
install %{name}-%{version}/skins/pro/*.props $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/pro
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/pro/images
install %{name}-%{version}/skins/pro/images/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/pro/images
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/spec
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/TargetSolver
install %{name}-%{version}/TargetSolver/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/TargetSolver
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Tool
install %{name}-%{version}/Tool/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Tool
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Tool/dtml
install %{name}-%{version}/Tool/dtml/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Tool/dtml
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
install %{name}-%{version}/www/*.png $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/www
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,zope,zope,0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt
%{_libdir}/zope/lib/python/Products/%{name}/
#----------------------------------------------------------------------
%changelog
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
