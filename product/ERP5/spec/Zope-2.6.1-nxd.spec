# File: zope.spec

Summary:    A leading open source application server.
Name:		Zope
Version:	2.6.1
Release:	8mdk
License:    Zope Public License (ZPL)
Group:		Networking/WWW
Vendor:     Zope Corp.
URL:        http://www.zope.org/
Packager:   Stéfane Fermigier, Nuxeo <sf@nuxeo.com>
Prereq:     rpm-helper

Source0:	http://www.zope.org/Products/Zope/%{version}/Zope-%{version}-src.tar.bz2
Source1:	http://www.zope.org/Members/michel/ZB/ZopeBook.tar.bz2
Source7:	Zope.init
Source8:	Zope-zserver.sh
Requires:	python >= 2.2
BuildRequires:	python-devel >= 2.2
BuildRoot:	%{_tmppath}/%{name}-%{version}-root-%(id -u -n)
Patch1: Zope-2.6.1.ftp.patch

%description
The Z Object Programming Environment (Zope) is a free, Open Source Python-based
application server for building high-performance, dynamic web sites, using a
powerful and simple scripting object model and high-performance, integrated
object database.


####
# Section: Prep Script (Prepare to Build; Usually Just Unpacking the Sources)
####
%prep
%setup -q -n Zope-%{version}-src
%patch1 -p1

# Prepare doc (Zope Book)
tar xjf %{SOURCE1}



####
# Section: Build Script (Actually Perform the Build; Usually Just 'make')
####
%build
perl -pi -e "s|data_dir\s+=\s+.*?join\(INSTANCE_HOME, 'var'\)|data_dir=INSTANCE_HOME|" lib/python/Globals.py
/usr/bin/python wo_pcgi.py

# Clean sources
find -type d -name "tests" | xargs rm -rf
find lib/python -type f -and \( -name 'Setup' -or -name '.cvsignore' \) \
    -exec rm -f \{\} \;
find -type f -and \( -name '*.c' -or -name '*.h' -or -name 'Makefile*' \) \
    -exec rm -f \{\} \;
find -name "Win32" | xargs rm -rf
rm -f ZServer/medusa/monitor_client_win32.py

# Has a bogus #!/usr/local/bin/python1.4 that confuses RPM
rm -f ZServer/medusa/test/asyn_http_bench.py

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_libdir}/zope/lib/python} \
    $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/log,/var/lib/zope}

cp -a lib/python/* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python
cp -a ZServer/ utilities/ import/ $RPM_BUILD_ROOT%{_libdir}/zope
find $RPM_BUILD_ROOT%{_libdir}/zope -type f -name '*.pyc' -or -name '*.txt' \
    | xargs -r rm -f
cp -a ZServer/medusa/test/* $RPM_BUILD_ROOT%{_libdir}/zope/ZServer/medusa/test/

install zpasswd.py $RPM_BUILD_ROOT%{_bindir}/zpasswd
install z2.py $RPM_BUILD_ROOT%{_libdir}/zope
install %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/zope-zserver
install %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/zope
install var/Data.fs $RPM_BUILD_ROOT/var/lib/zope/Data.fs

touch $RPM_BUILD_ROOT/var/log/zope

# XXX: shouldnt put a default password like this !
/usr/bin/python $RPM_BUILD_ROOT%{_bindir}/zpasswd -u zope -p zope -d localhost \
    $RPM_BUILD_ROOT/var/lib/zope/access

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%_pre_useradd zope /var/lib/zope /bin/false

%post
%_post_service zope

%preun
%_preun_service zope

%postun
%_postun_userdel zope

%files
%defattr(644,root,root,755)
%config(noreplace) %attr(755,root,root) /etc/rc.d/init.d/zope
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%{_libdir}/zope
%attr(1771,root,zope) %dir /var/lib/zope
%attr(660,root,zope) %config(noreplace) %verify(not md5 size mtime) /var/lib/zope/*
%attr(640,root,zope) /var/log/zope

##############################################################################

%package docs
Summary:    Documentation for the Zope application server
Requires:   Zope = %version-%release
Group:      Networking/WWW

%description docs
Documentation for the Z Object Programming Environment (Zope), a free, Open
Source Python-based application server for building high-performance, dynamic
web sites, using a powerful and simple scripting object model and
high-performance, integrated object database.

%files docs
%defattr(644,root,root,755)
%doc ZopeBook doc


##############################################################################

%changelog
* Thu May 27 2003 Sébastien Robin <seb@nexedi.com> 2.6.1-8mdk
  - Add new patch (to get source for ftp download)
    made by Jean-Paul Smets <jp@nexedi.com>

* Thu Apr 24 2003 Sébastien Robin <seb@nexedi.com> 2.6.1-7mdk
  - Keep *.py files and remove *.pyc files (better for developers)

* Thu Apr 24 2003 Sébastien Robin <seb@nexedi.com> 2.6.1-6mdk
  - Rename the package zope by Zope

* Mon Mar 24 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-5mdk
  - Moved python stuff from %{_libdir}/zope to %{_libdir}/zope/lib/python

* Tue Feb 25 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-4mdk
  - changes by Frederic Lepied 
  - fixed dependency problem between zope-docs and zope
  - removed unused directive

* Sun Feb 23 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-3mdk
  - fix bugs

* Sat Feb 22 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-2mdk
  - dont ship tests
  - separate docs package, including the Zope Book.

* Sat Feb 22 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-1mdk
  First release starting from PLD RPM.

