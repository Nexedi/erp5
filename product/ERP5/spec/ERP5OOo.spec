%define product ERP5OOo
%define version 0.11
%define release 3

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   OpenOffice documents parser for ERP5
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Conflicts: ERP5OOo
Requires:  erp5-zope

#----------------------------------------------------------------------
%description
General purpose tools to parse and handle OpenOffice v1.x documents in ERP5.

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
if [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%postun
if [ -f "%{_prefix}/bin/zopectl" ] && [ "`%{_prefix}/bin/zopectl status`" != "daemon manager not running" ] ; then
  service zope restart
fi

%files
%defattr(0644, root, root, 0755)
%doc %{product}/VERSION.txt
%{software_home}/Products/*

#----------------------------------------------------------------------
%changelog
* Mon Jan 30 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-3mdk
- New build from the CVS

* Fri Jan 27 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-2mdk
- New build from the CVS

* Thu Jan 26 2006 Kevin Deldycke <kevin@nexedi.com> 0.11-1mdk
- Update to version 0.11

* Wed Jan 18 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-1mdk
- Update to version 0.10

* Mon Jan 16 2006 Kevin Deldycke <kevin@nexedi.com> 0.2.20060116-1mdk
- New build from the CVS

* Tue Jan 10 2006 Kevin Deldycke <kevin@nexedi.com> 0.2-1mdk
- New release for Mandriva 2006
- Spec file updated

* Sat Apr 30 2005 Kevin Deldycke <kevin@nexedi.com> 0.1-1nxd
- Create the spec file
