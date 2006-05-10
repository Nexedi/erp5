%define product ERP5Subversion
%define version 0.12
%define release 2

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   A zope product to integrate SVN with ERP5 to make developer life easier.
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Conflicts: ERP5Subversion
Requires:  erp5-zope pysvn

#----------------------------------------------------------------------
%description
This zope product provides a Subversion interface to ERP5.

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
%defattr(0644, zope, zope, 0755)
%doc %{product}/VERSION.txt %{product}/README.txt
%{software_home}/Products/*

#----------------------------------------------------------------------
%changelog
* Fri May 05 2006 Kevin Deldycke <kevin@nexedi.com> 0.12-2mdk
- New build from the SVN repository

* Tue May 02 2006 Kevin Deldycke <kevin@nexedi.com> 0.12-1mdk
- New build from the SVN repository

* Tue May 02 2006 Kevin Deldycke <kevin@nexedi.com> 0
- Initial release
