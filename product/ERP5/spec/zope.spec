Name:       zope
Summary:    A leading open source application server
Version:    2.7.0rc1
Release:    1mdk
License:    Zope Public License (ZPL)
Group:      System/Servers
URL:        http://www.zope.org/
Packager:   Stéfane Fermigier, Nuxeo <sf@nuxeo.com>
Prereq:     rpm-helper

%define packagename Zope-2.7.0-rc1
%define python /usr/bin/python
%define zopehome /usr/lib/zope
%define softwarehome %{zopehome}/lib/python
%define instancehome /var/lib/zope
%define clienthome %{instancehome}/data
%define statehome /var/run/zope
%define loghome /var/log/zope
%define configfile /etc/zope.conf
%define zopectl /usr/bin/zopectl
%define runzope /usr/bin/runzope
%define zopeuser zope

# from http://www.zope.org/Products/Zope/%{version}/Zope-%{version}-%{release}.tgz
Source0:    %{packagename}.tar.bz2
Source1:    skel.tar.bz2
Source2:    http://www.zope.org/Members/michel/ZB/ZopeBook.tar.bz2
Requires:   python >= 2.2.3
BuildRequires:  python-devel >= 2.2.3
BuildRoot:  %{_tmppath}/%{name}-%{version}-root-%(id -u -n)

%description
The Z Object Programming Environment (Zope) is a free, Open Source,
Python-based application server for building high-performance, dynamic web
sites, using a powerful and simple scripting object model and high-performance,
integrated object database. It enables developers to quickly build web
applications such as intranets, portals, and content management systems.


%prep
%setup -q -n %{packagename}

# Add skel
rm -rf skel
tar xvjf %{SOURCE1}
#rm skel/var/log/zope/README.txt skel/var/run/zope/README.txt

# Prepare doc (Zope Book)
tar xjf %{SOURCE2} 


%build
mkdir -p build
pushd build
../configure \
  --with-python="%{python}" \
  --prefix="%{buildroot}%{zopehome}" \
  --no-compile
make build
popd

# process the skel directory into the buildroot
%{python} "utilities/copyzopeskel.py" \
         --sourcedir="skel" \
         --targetdir="%{buildroot}" \
         --replace="INSTANCE_HOME:%{instancehome}" \
         --replace="CLIENT_HOME:%{clienthome}" \
         --replace="STATE_DIR:%{statehome}" \
         --replace="LOG_DIR:%{loghome}" \
         --replace="SOFTWARE_HOME:%{softwarehome}" \
         --replace="ZOPE_HOME:%{zopehome}" \
         --replace="CONFIG_FILE:%{configfile}" \
         --replace="PYTHON:%{python}" \
         --replace="ZOPECTL:%{zopectl}" \
         --replace="RUNZOPE:%{runzope}"

#perl -pi -e "s|data_dir\s+=\s+.*?join\(INSTANCE_HOME, 'var'\)|data_dir=INSTANCE_HOME|" lib/python/Globals.py

python << EOF
import py_compile, os
files = os.popen("find . -name '*.py'").readlines()
for file in files:
    file = file.strip()
    py_compile.compile(file, file+"o", "%{zopehome}/"+file)
EOF

# XXX: next release...
#env CFLAGS="$RPM_OPT_FLAGS" /usr/bin/python setup.py build
#/usr/bin/python setup.py install --root=$RPM_BUILD_ROOT \
#    --record=INSTALLED_FILES

## Clean sources
#find -type d -name "tests" | xargs rm -rf
find lib/python -type f -and \( -name 'Setup' -or -name '.cvsignore' \) \
    -exec rm -f \{\} \;
#find -type f -and \( -name '*.c' -or -name '*.h' -or -name 'Makefile*' \) \
#    -exec rm -f \{\} \;
find -name "Win32" | xargs rm -rf
rm -f ZServer/medusa/monitor_client_win32.py

# Has a bogus #!/usr/local/bin/python1.4 that confuses RPM
rm -f ZServer/medusa/test/asyn_http_bench.py

%install
pushd build
make install
popd

#rm -rf $RPM_BUILD_ROOT
#install -d $RPM_BUILD_ROOT{%{_bindir},%{_sbindir},%{_libdir}/zope/lib/python} \
#    $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/log,/var/lib/zope}
#
#cp -a lib/python/* $RPM_BUILD_ROOT%{_libdir}/zope/lib/python
#cp -a ZServer/ utilities/ import/ $RPM_BUILD_ROOT%{_libdir}/zope
#find $RPM_BUILD_ROOT%{_libdir}/zope -type f -name '*.py' -or -name '*.txt' \
#    | xargs -r rm -f
#cp -a ZServer/medusa/test/* $RPM_BUILD_ROOT%{_libdir}/zope/ZServer/medusa/test/
#
#install zpasswd.py $RPM_BUILD_ROOT%{_bindir}/zpasswd
#install z2.py $RPM_BUILD_ROOT%{_libdir}/zope
#install %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/zope-zserver
#install %{SOURCE7} $RPM_BUILD_ROOT/etc/rc.d/init.d/zope
#install var/Data.fs $RPM_BUILD_ROOT/var/lib/zope/Data.fs
#
#touch $RPM_BUILD_ROOT/var/log/zope


%clean
rm -rf $RPM_BUILD_ROOT

%pre
%_pre_useradd zope /var/lib/zope /bin/false

%post
%_post_service zope

# write a 10 digit random default admin password into acl_users
passwd=`head -c4 /dev/urandom | od -tu4 -N4 | sed -ne '1s/.* //p'`
%{zopectl} adduser admin $passwd

/sbin/chkconfig --add zope

# inform the user of the default username/password combo and port
echo
echo A Zope instance has been installed.  Run it via
echo \"/etc/rc.d/init.d/zope start\".  Log in via a browser on port 9080.
echo
echo Zope has default administrative username/password combination.  The
echo "administrative username is \"admin\" and the password is \"$passwd\"."
echo Please remember this so you are able to log in for the first time.
echo


%preun
%_preun_service zope

%postun
%_postun_userdel zope

%files
%defattr(-,root,root)
%dir %{zopehome}
%{zopehome}/bin
%{zopehome}/doc
%{zopehome}/import
%{zopehome}/lib
%{zopehome}/skel
#%{zopehome}/utilities - XXX add this ?
%config /etc/zope.conf
/etc/logrotate.d/zope
/etc/rc.d/init.d/zope
/usr/bin/runzope
/usr/bin/zopectl
%attr(700, %{zopeuser}, %{zopeuser}) %config(noreplace) %verify(not md5 size mtime) %{instancehome}
%attr(755, %{zopeuser}, %{zopeuser}) %dir /var/log/zope
%attr(755, %{zopeuser}, %{zopeuser}) %dir /var/run/zope

#%defattr(644,root,root,755)
#%config(noreplace) %attr(755,root,root) /etc/rc.d/init.d/zope
#%attr(755,root,root) %{_bindir}/*
#%attr(755,root,root) %{_sbindir}/*
#%{_libdir}/zope
#%attr(1771,root,zope) %dir /var/lib/zope
#%attr(660,root,zope) %config(noreplace) %verify(not md5 size mtime) /var/lib/zope/*
##%attr(640,root,root) %ghost /var/log/zope
#%ghost /var/log/zope


##############################################################################

%package docs
Summary:    Documentation for the Zope application server
Requires:   zope = %version-%release
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
* Wed Jan 22 2004 Sebastien Robin <seb@nexedi.com> 2.7.0rc1-1mdk
  - udpated to version rc1

* Mon Sep 8 2003 Sebastien Robin <seb@nexedi.com> 2.7.0b1-2mdk
  - We use python2.3 instead of python2.2

* Sat Jul 26 2003 Stéfane Fermigier <sf@nuxeo.com> 2.7.0b1-1mdk
  - Update to Zope 2.7.0b1
  - Merged stuff from the Zope.org RPM

* Sat May 3 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-6mdk
  - Moved python stuff from /usr/lib/zope to /usr/lib/zope/lib/python

* Mon Mar 24 2003 Stéfane Fermigier <sf@nuxeo.com> 2.6.1-5mdk
  - Moved python stuff from /usr/lib/zope to /usr/lib/zope/lib/python

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

