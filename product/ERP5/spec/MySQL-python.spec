%define name MySQL-python
%define version 0.9.2
%define release 2mdk

Summary: Python interface to MySQL
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.bz2
License: GPL
Group: Development/Python
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
Vendor: MySQL-python SourceForge Project
Packager: Andy Dustman <andy@dustman.net>
Requires: python
Url: http://sourceforge.net/projects/mysql-python
Distribution: Red Hat Linux
BuildRequires: python-devel mysql-devel zlib-devel

%description
Python interface to MySQL-3.23

MySQLdb is an interface to the popular MySQL database server for Python.
The design goals are:

-     Compliance with Python database API version 2.0 
-     Thread-safety 
-     Thread-friendliness (threads will not block each other) 
-     Compatibility with MySQL-3.23 and later

This module should be mostly compatible with an older interface
written by Joe Skinner and others. However, the older version is
a) not thread-friendly, b) written for MySQL 3.21, c) apparently
not actively maintained. No code from that version is used in
MySQLdb. MySQLdb is free software.



%prep
%setup

%build
env CFLAGS="$RPM_OPT_FLAGS" python setup.py build

%install
python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README doc/*.?tml CHANGELOG

#----------------------------------------------------------------------
%changelog
* Mon Sep 08 2003 Sebastien Robin <seb@nexedi.com> 0.9.2-2mdk
- Update spec in order to follows Mandrake Rules

