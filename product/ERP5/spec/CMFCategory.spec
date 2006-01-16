%define product CMFCategory
%define version 0.9.20060116
# If we get the code from the CVS, the release will be always the first
%define release 1

%define zope_home %{_prefix}/lib/zope
%define software_home %{zope_home}/lib/python

Summary:   All algorithms related to categories and relations in CMF
Name:      zope-%{product}
Version:   %{version}
Release:   %mkrel %{release}
License:   GPL
Group:     System/Servers
URL:       http://www.erp5.org
Source0:   %{product}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-rootdir
BuildArch: noarch
Requires:  zope zope-CMF

#----------------------------------------------------------------------
%description
Category objects allow to define classification categories
in an ERP5 portal. For example, a document may be assigned a color
attribute (red, blue, green). Rather than assigning an attribute
with a pop-up menu (which is still a possibility), we can prefer
in certain cases to associate to the object a category. In this
example, the category will be named color/red, color/blue or color/green.

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
%doc VERSION.txt
%{software_home}/Products/*

#----------------------------------------------------------------------
%changelog
* Mon Jan 16 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060116-1mdk
- New build from the CVS

* Tue Jan 10 2006 Kevin Deldycke <kevin@nexedi.com> 0.9.20060110-1mdk
- New release for Mandriva 2006
- Spec file updated

* Tue Sep 01 2004 Sebastien Robin <seb@nexedi.com> 0.8-1mdk
- Final relase for Mandrake 10.1

* Mon Jun 14 2004 Sebastien Robin <seb@nexedi.com> 0.1-5mdk
- New release for Mandrake 10.1

* Tue Feb 17 2004 Sebastien Robin <seb@nexedi.com> 0.1-4mdk
- New release before mandrake 10

* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.1-3mdk
- Changed permissions on files

* Wed Sep 05 2003 Sebastien Robin <seb@nexedi.com> 0.1-2mdk
- Update spec in order to follows Mandrake Rules

* Mon May 12 2003 Sebastien Robin <seb@nexedi.com> 0.1-1nxd
- Create the spec file
