# File: Base18.spec
#
# Base18
#
#   "Base18 is a Zope product to implement multilingual portals
#    based on the Zope CMF"
#
# This product currently packages the code 


%define PRODUCT_DIRECTORY /var/lib/zope/Products
%define USER  jp

Name:               Base18
Summary:            A Zope product to implement multilingual portals with CMF
Version:            0.2.0
Release:            10nxd
Group:              Development/Python
Requires:           Zope Localizer CMF
Copyright:          GPL
Vendor:             Nexedi
URL:                http://www.erp5.org
Packager:           Jean-Paul Smets <jp@nexedi.com>
BuildRoot:          /var/tmp/%{name}-%{version}-rootdir

Source0: http://www.erp5.org/download/%{name}-%{version}.tar.bz2
Source1: %{name}-%{version}.tar.bz2

#----------------------------------------------------------------------
%description
Base18 is a Zope product to implement multilingual portals
It extends the Zope CMF by allowing documents to be split into
a list of paragraphs which can be translated through a message catalog.
Thanks to Localizer, messages are stored in message catalogs which
can be exported and imported as gettext files. This allows to use
applications such as KBabel to search for previous translations of
a give sentence.

http://www.erp5.org

#----------------------------------------------------------------------
%prep

#Create the source code from the local Zope
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
install %{name}-%{version}/*.png $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}
install %{name}-%{version}/*.zexp $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/help
install %{name}-%{version}/help/*.stx $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/help

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/dtml
install %{name}-%{version}/dtml/*.dtml $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/dtml

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.py $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.pt $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.dtml $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.props $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.png $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi
install %{name}-%{version}/skins/nexedi/*.ico $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/content18
install %{name}-%{version}/skins/content18/*.py $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/content18
install %{name}-%{version}/skins/content18/*.dtml $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/content18

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/zpt_nexedi
install %{name}-%{version}/skins/zpt_nexedi/*.pt $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/zpt_nexedi

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/zpt_content18
install %{name}-%{version}/skins/zpt_content18/*.pt $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/skins/zpt_content18

install -d $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/interfaces
install %{name}-%{version}/interfaces/*.py $RPM_BUILD_ROOT/usr/lib/zope/lib/python/Products/%{name}/interfaces


%clean
rm -rf $RPM_BUILD_ROOT

#----------------------------------------------------------------------
%files
%defattr(-,root,root,0755)
%doc README.txt INSTALL.txt CREDITS.txt GPL.txt ZPL.txt

/usr/lib/zope/lib/python/Products/%{name}/*.py
/usr/lib/zope/lib/python/Products/%{name}/interfaces/*.py
/usr/lib/zope/lib/python/Products/%{name}/*.txt
/usr/lib/zope/lib/python/Products/%{name}/*.png
/usr/lib/zope/lib/python/Products/%{name}/*.zexp
/usr/lib/zope/lib/python/Products/%{name}/help/*.stx
/usr/lib/zope/lib/python/Products/%{name}/dtml/*.dtml
/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi/*.dtml
/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi/*.py
/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi/*.pt
/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi/*.png
/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi/*.props
/usr/lib/zope/lib/python/Products/%{name}/skins/nexedi/*.ico
/usr/lib/zope/lib/python/Products/%{name}/skins/content18/*.dtml
/usr/lib/zope/lib/python/Products/%{name}/skins/content18/*.py
/usr/lib/zope/lib/python/Products/%{name}/skins/zpt_nexedi/*.pt
/usr/lib/zope/lib/python/Products/%{name}/skins/zpt_content18/*.pt

#----------------------------------------------------------------------
%changelog
* Tue Feb 4 2003 Jean-Paul Smets <jp@nexedi.com> 0.8.1-10nxd
- Updated description

* Thu Jan 30 2003 Jean-Paul Smets <jp@nexedi.com> 0.8.1-9nxd
- Missing interfaces

* Tue Jan 21 2003 Jean-Paul Smets <jp@nexedi.com> 0.8.1-8nxd
- Missing menu_box

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.8.1-7nxd
- Fixed again missing skins

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.8.1-6nxd
- Fixed again missing skins

* Wed Jan 8 2003 Jean-Paul Smets <jp@nexedi.com> 0.8.1-5nxd
- Code update for latest CMF - recover from crash

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com> 0.8.1-1nxd
- Initial release
