# File: Coramy.spec
#
# Coramy
#
#   "ERP5 is a Zope framework which allows to implement ERP software."
#

Name:               Coramy
Summary:            The ERP5 implementation for Coramy
Version:            0.1
Release:            2nxd
Group:              Development/Python
Requires:           ERP5 zope
License:            GPL
Vendor:             Nexedi
URL:                http://www.erp5.org
Packager:           Sebastien Robin <seb@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Buildarch:          noarch

Source: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
This is an implementation of ERP5, an Free entreprise resource
management solution.

#----------------------------------------------------------------------
%prep

rm -rf $RPM_BUILD_ROOT
%setup -a 0

#----------------------------------------------------------------------
%build

#----------------------------------------------------------------------
%install
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install %{name}-%{version}/*.txt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install %{name}-%{version}/Constraint/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Constraint
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install %{name}-%{version}/Document/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Document
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install %{name}-%{version}/Extensions/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Extensions
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.css $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.html $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help/images
install %{name}-%{version}/help/images/*.gif $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help/images
install %{name}-%{version}/help/images/*.jpg $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/help/images
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install %{name}-%{version}/Interface/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/Interface
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install %{name}-%{version}/PropertySheet/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/PropertySheet
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_crm
install %{name}-%{version}/skins/coramy_crm/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_crm
install %{name}-%{version}/skins/coramy_crm/*.dtml $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_crm
install %{name}-%{version}/skins/coramy_crm/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_crm
install %{name}-%{version}/skins/coramy_crm/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_crm
install %{name}-%{version}/skins/coramy_crm/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_crm
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_custom
install %{name}-%{version}/skins/coramy_custom/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_custom
install %{name}-%{version}/skins/coramy_custom/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_custom
install %{name}-%{version}/skins/coramy_custom/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_custom
install %{name}-%{version}/skins/coramy_custom/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_custom
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_erp5
install %{name}-%{version}/skins/coramy_erp5/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_erp5
install %{name}-%{version}/skins/coramy_erp5/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_erp5
install %{name}-%{version}/skins/coramy_erp5/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_erp5
install %{name}-%{version}/skins/coramy_erp5/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_erp5
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_list_method
install %{name}-%{version}/skins/coramy_list_method/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_list_method
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_manufacturing
install %{name}-%{version}/skins/coramy_manufacturing/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_manufacturing
install %{name}-%{version}/skins/coramy_manufacturing/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_manufacturing
install %{name}-%{version}/skins/coramy_manufacturing/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_manufacturing
install %{name}-%{version}/skins/coramy_manufacturing/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_manufacturing
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_mrp
install %{name}-%{version}/skins/coramy_mrp/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_mrp
install %{name}-%{version}/skins/coramy_mrp/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_mrp
install %{name}-%{version}/skins/coramy_mrp/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_mrp
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_pdm
install %{name}-%{version}/skins/coramy_pdm/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_pdm
install %{name}-%{version}/skins/coramy_pdm/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_pdm
install %{name}-%{version}/skins/coramy_pdm/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_pdm
install %{name}-%{version}/skins/coramy_pdm/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_pdm
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_trade
install %{name}-%{version}/skins/coramy_trade/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_trade
install %{name}-%{version}/skins/coramy_trade/*.pt $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_trade
install %{name}-%{version}/skins/coramy_trade/*.form $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_trade
install %{name}-%{version}/skins/coramy_trade/*.zsql $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/skins/coramy_trade
install -d $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
install %{name}-%{version}/tests/*.py $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/Products/%{name}/tests
%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc VERSION.txt
%{_libdir}/zope/lib/python/Products/%{name}/
#----------------------------------------------------------------------
%changelog
* Mon Apr 28 2002 Sebastien Robin <seb@nexedi.com> 0.1.0-1nxd
- Initial release
