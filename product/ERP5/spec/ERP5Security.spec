%define product ERP5Security
%define version 0.10
%define release 1

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   A collection of plugins for Pluggable Auth Service to manage ERP5 security
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Requires:  erp5-zope zope-PluggableAuthService

#----------------------------------------------------------------------
%description
This zope product is a plugin to Pluggable Auth Service, to manage roles,
groups and users in ERP5. It also add fine security management features to
ERP5.

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
* Wed Jan 18 2006 Kevin Deldycke <kevin@nexedi.com> 0.10-1mdk
- Update to version 0.10

* Mon Jan 16 2006 Kevin Deldycke <kevin@nexedi.com> 0.1.20060116-1mdk
- New build from the CVS

* Tue Jan 10 2006 Kevin Deldycke <kevin@nexedi.com> 0.1.20060110-1mdk
- Initial release
