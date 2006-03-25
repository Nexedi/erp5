# File: Zope-2.5.1-nxd.spec
#
# Digicool Z-Object Programming Environment (ZOPE)
#
#   "Zope is an Open Source application server and portal
#    toolkit used for building high-performance, dynamic Web sites."
#
# An independent 'BuildRoot:' directive is used so that that this package
# can be built in the %{_tmppath} directory, for the case where the existing
# software on the build host would be disrupted by installing-after-build-
# to-package onto that system.
#
# Sample Package Names:
#   Zope-2.5.1-1nxd.i386.rpm
#
# NOTE to Future ZOPE RPM Maintainers:
#
# The Zope tarball contains many subsystems, some dependent on Zope and
# some that can be used independently.  The independent ones have been
# placed into the common %{_libdir}/python2.1/site-packages/ directory tree
# while for the others, I've created a new directory:
#
#     %{_libdir}/zope/
#
# The contents of that directory is -not- a Python Package such that
# anyone must "import blah".  Rather, it is directly imported by the Zope
# software.  This does mean naming collisions are possible with non-Zope
# packages such as PIL and mxDateTime, but until Zope is reorganized into
# a true Python Package layout, this cannot be helped.
#
# The %{_libdir}/zope/ hierarchy is read-only, while the /var/lib/zope/ one is
# basically read-write, in keeping with the Linux Filesystem Standard.
#
####

# Notify ZC of needed removal of zlib module
# Ask ZC about conflict of pyexpat in Zope and Py2.1.1

# To-Be-Done-Perhaps:
#o work to make compatible with other distributions: RH 6.2 and RH 7.0 (no rc.d) and Caldera, etc.
#o add ZServer-fastcgi sub-RPM
#o cause zserver*sh scripts to take the name of the python interpreter from %{PYTHONAPP};
#  also need to handle REQUIRE: directive as either python or python2 or python3.

####
# Section: Preamble (Items Displayed When Users Request Info About Package)
#
# The order of the entries below is unimportant.
#
####

%define PYTHONAPP /usr/bin/python2.1
%define PYTHONDIR python2.1

Name:               Zope
Version:            2.5.1
Release:            4nxd
License:          Zope Public License (ZPL)
Vendor:             Zope Corporation
URL:                http://www.zope.org/
Packager:           Jean-Paul Smets <jp@nexedi.com>
BuildRoot:          %{_tmppath}/%{name}-%{version}-rootdir
Prereq:             python2.1 python2.1-devel /sbin/chkconfig /usr/sbin/useradd

Source0: http://www.zope.org/Download/Releases/%{name}-%{version}/Zope-%{version}-src.tgz
###Source1: http://www.zope.org/Documentation/Guides/ZCMG/ZCMG.html.tgz
###Source2: http://www.zope.org/Documentation/Guides/DTML/DTML.html.tgz
###Source3: http://www.zope.org/Documentation/Guides/ZSQL/ZSQL.html.tgz
###Source4: http://www.zope.org/Documentation/Guides/Zope-ProductTutorial.tar.gz
Source5: Zope-%{version}-zope
Source6: Zope-%{version}-Zope.cgi
Source7: Zope-%{version}-README.RPM
Source8: Zope-%{version}-zserver-wo-pcgi.sh
Source9: Zope-%{version}-zserver-w-pcgi.sh
###Source10: http://www.zope.org/Documentation/Guides/ZDG/ZDG.html.tgz
###Source11: http://www.zope.org/Documentation/Guides/ZAG/ZAG.html.tgz
Source12: Zope-%{version}-pcgi_nullpublisher.py
Source13: Makefile.pre.in
###Source14: Zope-%{version}-index.html
Source16: Hotfix_2002-04-15.tgz
Patch3: Zope-%{version}-pcgi-syslog.patch
Patch4: Zope-%{version}-tal-i18n.patch

#----------------------------------------------------------------------
Summary:            An application server and portal toolkit for building Web sites.
Group:              Development/Python
Requires:           python2.1 >= 2.1
%description
The Z Object Programming Environment (Zope) is a free, Open Source[tm]
Python-based application server for building high-performance, dynamic
web sites, using a powerful and simple scripting object model and
high-performance, integrated object database.

Brian Lloyd's excellent article, An Introduction to Zope
(http://www.devshed.com/Server_Side/Zope/Intro/) provides a great starting
point to understanding what Zope is and how you can use it.

For a fully functional installation of Zope, install this single huge
package and then _either_ the Zope-zserver RPM, for a minimal Python-based
web server; or the Zope-pcgi RPM, for use with Apache's CGI facility.

If you only want portions of Zope, there are subpackages available
for each subsystem and you should _not_ install this RPM.

#----------------------------------------------------------------------
%package core
Summary:            Central Core of Zope w/General Extensions
Group:              Development/Python
Requires:           python2.1 >= 2.1, Zope-components, Zope-ztemplates, Zope-zpublisher, Zope-services
Conflicts:          Zope

%description core
The Z Object Programming Environment (Zope) is a free, Open Source[tm]
Python-based application server for building high-performance, dynamic
web sites, using a powerful and simple scripting object model and
high-performance, integrated object database.

Brian Lloyd's excellent article, An Introduction to Zope
(http://www.devshed.com/Server_Side/Zope/Intro/) provides a great starting
point to understanding what Zope is and how you can use it.

The Zope-core package contains the central core programs and general
extensions needed to run Zope.

For a fully functional installation of Zope, install Zope, Zope-components,
Zope-core, Zope-services, Zope-zpublisher, and Zope-ztemplates, and one of
the following packages: Zope-zserver, for a minimal Python-based Web
server; or Zope-pcgi, for using Zope with Apache's CGI facility.

#----------------------------------------------------------------------
%package components
Summary:            A group of standalone Python binary extension modules.
Group:              Development/Python
Requires:           python2.1 >= 2.1
Conflicts:          Zope

%description components
The Zope-components package includes a group of standalone Python extension
modules, including BTree, ExtensionClass, Acquisition, MethodObject,
MultiMapping, ThreadLock, Missing, Sync, Record, ComputedAttribute and
RestrictedPython.  These modules can be used with the Zope application
server and portal toolkit or standalone.

#----------------------------------------------------------------------
%package ztemplates
Summary:            A template for creating dynamic HTML for Zope.
Group:              Development/Python
Requires:           python2.1 >= 2.1
Conflicts:          Zope

%description ztemplates
The Zope-ztemplates package contains a Python-based template mechanism for
creating dynamic HTML sources, with Python expressions, looping constructs,
etc. The Z Template system can be used with the Zope application server and
portal tookit, or it can be used standalone. Z Template was called
DocumentTemplate in the olden days (before Zope).

#----------------------------------------------------------------------
%package zpublisher
Summary:            An object publishing mechanism for Zope.
Group:              Development/Python
Requires:           python2.1 >= 2.1, Zope-components >= 2.5.1
Conflicts:          Zope

%description zpublisher
Zpublisher is a Python-based object publishing mechanism that maps URLs
to an object hierarchy and handles the interface between the Web server
and the Web application, hiding many complex details.  Zpublisher is
used with the Zope application server and portal toolkit, but it can be
used standalone as well.  Zpublisher was called Bobo before Zope came along.


#----------------------------------------------------------------------
%package services
Summary:            Middle-level services for Zope.
Group:              Development/Python
Requires:           python2.1 >= 2.1, Zope-components >= 2.5.1
Conflicts:          Zope

%description services
The Zope-services package contains a group of middle-level services needed
by the Zope application server and portal toolkit (but not specifically
tied to Zope). Services included are DateTime, SearchIndex and
StructuredText.


#----------------------------------------------------------------------
%package zserver
Summary:            Initial Object Database/Standalone HTTP Server
Group:              Development/Python
Requires:           Zope
Conflicts:          Zope-pcgi
Provides:						Zope-webserver
#Prereq: /etc/init.d

%description zserver
The Zope-zserver package contains the files needed for setting up a
Zope website, including an empty object database. Zope is an application
server and portal toolkit.

Also included is the ZServer, which is a small, standalone web server
written in Python.  The ZServer uses the very fast Medusa technology
and is multithreaded.  This package comes preconfigured to serve
web pages on port 8080 and ftp access on 8021.  The programmer's port
interface comes disabled for security reasons but can be reenabled.

If you wish to instead run Zope thru Apache, do not use this package
but rather the Zope-pcgi package.  This package is for -standalone-
web serving.

#----------------------------------------------------------------------
%package pcgi
Summary:            Persistent CGI (PCGI) capabilities for Zope.
Group:              Applications/Internet
Requires:           Zope, apache >= 1.3
Conflicts:          Zope-zserver
URL:                http://starship.python.net/crew/jbauer/persistcgi/
Provides:						Zope-webserver
#Prereq: /etc/init.d 

%description pcgi
Persistent CGI (PCGI) is an architecture designed by Digital Creations
(http://www.digicool.com) for publishing Web objects as long-running
server processes in order to improve the performance of serving Web
pages.  This package is PCGI for use with the Zope application server
and portal toolkit.

It is not necessary for ZServer to actually listen for incoming HTTP
requests.  If you want Apache to do the actual listening and serving,
then you can use ZServer's PCGI component to communicate with Apache.

Please note that versions of the Apache Web server prior to 1.3 do not
have a sufficiently implemented rewrite module to provide authentication
for Zope.  You'll need to upgrade your Apache if you're using a version
prior to 1.3.

For PCGI HOWTO information, see:
    http://starship.python.net/crew/jbauer/persistcgi/

##########
#
# The following environment variables are automatically defined for use
# in any of the following shell scripts:
#
#   RPM_SOURCE_DIR      { where sources originally reside }
#   RPM_BUILD_DIR       { where sources get unpacked into }
#   RPM_DOC_DIR
#   RPM_OPT_FLAGS
#   RPM_ARCH
#   RPM_OS
#   RPM_ROOT_DIR
#   RPM_BUILD_ROOT      { where final images get placed before packaging }
#   RPM_PACKAGE_NAME
#   RPM_PACKAGE_VERSION
#   RPM_PACKAGE_RELEASE
#
##########

####
# Section: Prep Script (Prepare to Build; Usually Just Unpacking the Sources)
####
%prep
# Create Build Subdirectory and Unpack the Main Tar Ball
%setup -q -n %{name}-%{version}-src

### setup -q -T -D -c -a 1 -n %{name}-%{version}-src/ZopeContentManagersGuide
### setup -q -T -D -c -a 2 -n %{name}-%{version}-src/GuideToDTML
### setup -q -T -D -c -a 3 -n %{name}-%{version}-src/GuideToZSQL
### setup -q -T -D -c -a 10 -n %{name}-%{version}-src/ZopeDevelopersGuide
### setup -q -T -D -c -a 11 -n %{name}-%{version}-src/ZopeAdminGuide

# Current Hotfix(es), if Present
%setup -q -T -D -c -a 16 -n %{name}-%{version}-src

### setup -q -T -D    -a 4 -n %{name}-%{version}-src

# Reset RPM's Concept of "-n" Back to the Top-Level Package Dir Name
%setup -q -T -D -n %{name}-%{version}-src

%patch3 -p1
%patch4 -p1
## %patch4 -p1

## %patch5 -p1

# Create a Temporary Holding Area in the RPM's Build Directory for Docs
mkdir misc

# Some of the docs incorrectly have the 'Execute' bit set on their files
# so we do this for security reasons (and we can't use chmod -R if we
# want to only change files modes and not those of subdirectories) ;-(
### find ZopeContentManagersGuide -type f -exec chmod 644 \{\} \;
### find GuideToDTML              -type f -exec chmod 644 \{\} \;
### find GuideToZSQL              -type f -exec chmod 644 \{\} \;
### find Tutorial                 -type f -exec chmod 644 \{\} \;

####
# Section: Build Script (Actually Perform the Build; Usually Just 'make')
####
%build
  cp %{SOURCE7} $RPM_BUILD_DIR/%{name}-%{version}-src/README.RPM

  echo Building the PCGI Wrapper...
  (cd pcgi
  ./configure --prefix=/usr
  make)

  echo Building Zope Extension Modules...

  # Set up an easily-accessible Makefile template
  cp %{SOURCE13}  Makefile.pre.in

#jrr   cp Makefile.pre.in lib/python/Shared/DC/xml/pyexpat/Makefile.pre.in

  cp Makefile.pre.in lib/Components/BTree/
  cp Makefile.pre.in lib/Components/ExtensionClass/

  cp Makefile.pre.in lib/python/BTrees/
  cp Makefile.pre.in lib/python/DocumentTemplate/
  cp Makefile.pre.in lib/python/SearchIndex/
  cp Makefile.pre.in lib/python/ZODB/

  cp Makefile.pre.in lib/python/Shared/DC/xml/pyexpat/

  cp Makefile.pre.in lib/python/Products/PluginIndexes/TextIndex/Splitter/ISO_8859_1_Splitter/
  cp Makefile.pre.in lib/python/Products/PluginIndexes/TextIndex/Splitter/ZopeSplitter/
  cp Makefile.pre.in lib/python/Products/PluginIndexes/TextIndex/Splitter/UnicodeSplitter/

  # === General Loadable-Binary-Library Python Components ===

  # dcpyexpat.so
  pushd lib/python/Shared/DC/xml/pyexpat
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make CFLAGS="-I/usr/include/%{PYTHONDIR}/"
    make clean
    rm -rf expat
    mv README   $RPM_BUILD_DIR/%{name}-%{version}-src/misc/pyexpat.README
    find . -type f -not -name '*.py' -not -name '*.so' -exec rm \{\} \;
  popd

  # BTree.so IIBTree.so IOBTree.so OIBTree.so intSet.so
  pushd lib/Components/BTree
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make CFLAGS="-I../../python/ZODB/ -I/usr/include/%{PYTHONDIR}/"
    make clean
  popd

  # ExtensionClass.so Acquisition.so MethodObject.so MultiMapping.so
  # ThreadLock.so Missing.so Sync.so Record.so ComputedAttribute.so
  pushd lib/Components/ExtensionClass
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    cd src
    make -f ../Makefile
    make -f ../Makefile clean
    mv *.so ..
    cd ..
    
#broken %{PYTHONAPP} setup.py build

    # Separate out docs from code for a cleaner RPM build
    mkdir ExtensionClass
    mv doc/ test/ COPYRIGHT.txt README  ExtensionClass
  popd

  # === Zope Subsystems ===

  # cDocumentTemplate.so
  pushd lib/python/DocumentTemplate
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -not -name '*.stx' -exec rm \{\} \;
  popd

  # _IIBTree.so _IOBTree.so _OIBTree.so _OOBTree.so
  pushd lib/python/BTrees
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -exec rm \{\} \;
  popd
  # Note: The building of lib/python/BTrees _must_ come before building of ZODB (below)

  # TimeStamp.so cPersistence.so cPickleCache.so winlock.so coptimizations.so
  pushd lib/python/ZODB
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -not -name '*.gif' -not -name '*.html' -not -name '*.stx' -not -name 'cPersistence.h' -exec rm \{\} \;
  popd

  # Splitter.so(obsolete) Query.so
  pushd lib/python/SearchIndex
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -exec rm \{\} \;
  popd


  # (ISO_8859_1, Unicode and Zope Versions of) Splitter.so
  pushd lib/python/Products/PluginIndexes/TextIndex/Splitter
    rm -f setup.py

    cd ISO_8859_1_Splitter
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -exec rm \{\} \;
    rm -rf src

    cd ../ZopeSplitter
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -exec rm \{\} \;
    rm -rf src

    cd ../UnicodeSplitter
    make -f Makefile.pre.in boot PYTHON=%{PYTHONAPP}
    make
    make clean
    find . -type f -not -name '*.py' -not -name '*.so' -exec rm \{\} \;
    rm -rf src
  popd

   # Separate out docs from code for a cleaner RPM build
  pushd ZServer/medusa
    mkdir medusa
    mv docs/                                           medusa
    mv ANNOUNCE.txt  ANNOUNCE_970922.txt  INSTALL.txt  medusa
    mv contrib/  demo/  dist/  misc/  notes/           medusa
    mv script_handler_demo/  sendfile/                 medusa
    rm out  monitor_client_win32.py  Makefile
  popd

  # Remove Non-Release Items Before Copying Dirs
  # into Package, to Minimize Package Size

  find lib/python -type f -and \( -name 'Setup' -or -name '.cvsignore' -or -name 'Makefile' \) -exec rm \{\} \;


####
# Section: Install-After-Build Script (Often Just 'make install')
####
%install
  rm -rf $RPM_BUILD_ROOT

  # Make the Necessary Directories
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/site-packages
###  install -m0755 --directory      $RPM_BUILD_ROOT/var/www/html/zopedocs

  # Directory Structure for SOFTWARE_HOME=%{_libdir}/zope/
  install -m0755 --directory      $RPM_BUILD_ROOT/usr/bin
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/import
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/lib
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/lib/python
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/Extensions
  install -m0755 --directory      $RPM_BUILD_ROOT/usr/include/%{PYTHONDIR}
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/utilities
  install -m0755 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/ZODB

  # Directory Structure for INSTANCE_HOME=/var/lib/zope/
  install -m0755 --directory      $RPM_BUILD_ROOT/etc/rc.d/init.d
  install -m0775 --directory      $RPM_BUILD_ROOT/var/lib/zope
  install -m0775 --directory      $RPM_BUILD_ROOT/var/lib/zope/Extensions
  install -m0711 --directory      $RPM_BUILD_ROOT/var/lib/zope/var
  install -m0775 --directory      $RPM_BUILD_ROOT/var/lib/zope/Products
  install -m0775 --directory      $RPM_BUILD_ROOT/var/log
  install -m0775 --directory      $RPM_BUILD_ROOT%{_libdir}/zope/ZServer

  pushd lib/Components
    install -m0644 ExtensionClass/*.py  $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/
    install -m0644 ExtensionClass/src/ExtensionClass.h  $RPM_BUILD_ROOT/usr/include/%{PYTHONDIR}/
    install -s     ExtensionClass/*.so  $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/site-packages/
    install -s     BTree/*.so           $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/site-packages/
  popd

# distuils form of ExtensionClass is broken in 2.4.1
#  pushd lib/Components/ExtensionClass
#    %{PYTHONAPP} setup.py install --root $RPM_BUILD_ROOT
#  popd

###  install                              $RPM_SOURCE_DIR/%{name}-%{version}-index.html \
###                                       $RPM_BUILD_ROOT/var/www/html/zopedocs/index.html

###  cp -Rdp ZopeContentManagersGuide/    $RPM_BUILD_ROOT/var/www/html/zopedocs/
###  cp -Rdp GuideToZSQL/                 $RPM_BUILD_ROOT/var/www/html/zopedocs/
###  cp -Rdp GuideToDTML/                 $RPM_BUILD_ROOT/var/www/html/zopedocs/
###  cp -Rdp Tutorial/                    $RPM_BUILD_ROOT/var/www/html/zopedocs/
###  cp -Rdp ZopeDevelopersGuide/         $RPM_BUILD_ROOT/var/www/html/zopedocs/
###  cp -Rdp ZopeAdminGuide/              $RPM_BUILD_ROOT/var/www/html/zopedocs/

  cp -Rdp ZServer/                     $RPM_BUILD_ROOT%{_libdir}/zope/
  rm -rf                               $RPM_BUILD_ROOT%{_libdir}/zope/ZServer/medusa/medusa/

  cp -Rdp utilities/                   $RPM_BUILD_ROOT%{_libdir}/zope/
  cp -Rdp import/                      $RPM_BUILD_ROOT%{_libdir}/zope/
  install -m 0755 zpasswd.py           $RPM_BUILD_ROOT/usr/bin/zpasswd
  install -m 0755 zpasswd.py           $RPM_BUILD_ROOT%{_libdir}/zope/utilities/

  cp Extensions/README.txt             $RPM_BUILD_ROOT%{_libdir}/zope/Extensions/
  cp Extensions/README.txt             $RPM_BUILD_ROOT/var/lib/zope/Extensions/

  pushd lib/python
    # These are generally useful modules, (relatively) independent of Zope
    for i in DocumentTemplate/ SearchIndex/ ZPublisher/ DateTime/ BTrees/ \
             StructuredText/ RestrictedPython/
    do
       cp -Rdp $i $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/site-packages/
    done

    # These are integral parts of Zope and can't really stand alone
    cp    version.txt                   $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/

    for i in Zope/ AccessControl/ App/ HelpSys/ OFS/ TreeDisplay/  \
             ZClasses/ Shared/ Products/ ZODB/ webdav/ ZLogger/    \
             Interface/ Testing/ Persistence/ TAL/ ThreadedAsync/  \
             zdaemon/ zExceptions/ zLOG/ ZTUtils/
    do 
       cp -Rdp $i $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/
    done

    install -m0644 *.py                 $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/
    install -m0644 ZODB/cPersistence.h  $RPM_BUILD_ROOT/usr/include/%{PYTHONDIR}/
    rm             $RPM_BUILD_ROOT%{_libdir}/zope/lib/python/ZODB/cPersistence.h
  popd

  install -m 0755 -s pcgi/pcgi-wrapper  $RPM_BUILD_ROOT/usr/bin/pcgi-wrapper
  install pcgi/pcgi_publisher.py        $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/pcgi_publisher.py
  install pcgi/Util/killpcgi.py         $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/killpcgi.py

  install                               $RPM_SOURCE_DIR/%{name}-%{version}-pcgi_nullpublisher.py  \
                                        $RPM_BUILD_ROOT/var/lib/zope/pcgi_nullpublisher.py

  # Establish an Empty Zope Object Database
  install -m 0600 var/Data.fs.in        $RPM_BUILD_ROOT/var/lib/zope/var/Data.fs

  # Create a Safe Preowned Zope Logfile, for ZServer
  # (Otherwise a symlink-redirect attack may be possible!)
  touch $RPM_BUILD_ROOT/var/log/zope

  # Declare the Superuser of the Default Zope Project
  %{PYTHONAPP} $RPM_BUILD_ROOT/usr/bin/zpasswd -u superuser -p 123 -d localhost $RPM_BUILD_ROOT/var/lib/zope/access
  chmod 0640 $RPM_BUILD_ROOT/var/lib/zope/access

  install -m 0755 %{SOURCE5} $RPM_BUILD_ROOT/etc/rc.d/init.d/zope
  install -m 0755 %{SOURCE6} $RPM_BUILD_ROOT/var/lib/zope/Zope.cgi
  install -m 0755 %{SOURCE8} $RPM_BUILD_ROOT/var/lib/zope/zserver_wo_pcgi.sh
  install -m 0755 %{SOURCE9} $RPM_BUILD_ROOT/var/lib/zope/zserver_w_pcgi.sh
  install -m 0755 z2.py      $RPM_BUILD_ROOT/var/lib/zope/z2.py

  # Precompile Python Source for Faster Imports During Usage
  # (Since user of package may not have write-access to install directory)
  %{PYTHONAPP} -O %{_libdir}/%{PYTHONDIR}/compileall.py    -d %{_libdir}/%{PYTHONDIR}/  $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}
  %{PYTHONAPP}    %{_libdir}/%{PYTHONDIR}/compileall.py    -d %{_libdir}/%{PYTHONDIR}/  $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}

  %{PYTHONAPP} -O %{_libdir}/%{PYTHONDIR}/compileall.py    -d %{_libdir}/zope/     $RPM_BUILD_ROOT%{_libdir}/zope
  %{PYTHONAPP}    %{_libdir}/%{PYTHONDIR}/compileall.py    -d %{_libdir}/zope/     $RPM_BUILD_ROOT%{_libdir}/zope

  # Remove Duplicate Documentation Embedded in Python Package Dirs
  pushd $RPM_BUILD_ROOT%{_libdir}/zope
    rm     lib/python/AccessControl/AccessControl.txt
    rm     lib/python/Products/ZCatalog/ZCatalog.txt
    rm     ZServer/INSTALL.txt
    rm     ZServer/README.txt
  popd

  pushd $RPM_BUILD_ROOT%{_libdir}/%{PYTHONDIR}/site-packages
    rm     DateTime/DateTime.html
    rm     DocumentTemplate/Let.stx
    rm -rf StructuredText/regressions/
  popd

####
# Section: Delivery Install/Uninstall Scripts (Pre/Post Install/Erase Scripts)
####

%pre zserver
  /usr/sbin/useradd -M -r -s /bin/bash -d /var/lib/zope -c "Zope Server" zope >/dev/null 2>&1 || :
  
%pre pcgi
  /usr/sbin/useradd -M -r -s /bin/bash -d /var/lib/zope -c "Zope Server" zope >/dev/null 2>&1 || :

%post zserver
  /sbin/chkconfig --add zope
  ln -sf /var/lib/zope/zserver_wo_pcgi.sh /var/lib/zope/zserver.sh
  ln -sf %{_libdir}/zope/import /var/lib/zope/import

%post pcgi
  /sbin/chkconfig --add zope
  ln -sf /var/lib/zope/zserver_w_pcgi.sh /var/lib/zope/zserver.sh
  ln -sf %{_libdir}/zope/import /var/lib/zope/import

%preun zserver
  if [ "$1" = 0 ] ; then
    if [ /var/lib/zope/zserver_wo_pcgi.sh -ef /var/lib/zope/zserver.sh ]; then
      rm /var/lib/zope/zserver.sh
    fi
    if [ %{_libdir}/zope/import -ef /var/lib/zope/import ]; then
      rm /var/lib/zope/import
    fi
    /etc/rc.d/init.d/zope stop > /dev/null 2>&1
    /sbin/chkconfig --del zope
  fi

%preun pcgi
  if [ "$1" = 0 ] ; then
    if [ /var/lib/zope/zserver_w_pcgi.sh -ef /var/lib/zope/zserver.sh ]; then
      rm /var/lib/zope/zserver.sh
    fi
    if [ %{_libdir}/zope/import -ef /var/lib/zope/import ]; then
      rm /var/lib/zope/import
    fi
    /etc/rc.d/init.d/zope stop > /dev/null 2>&1
    /sbin/chkconfig --del zope
  fi

%postun zserver
  if [ $1 = 0 ] ; then
	userdel zope >/dev/null 2>&1 || :
  fi
  if [ "$1" -ge "1" ]; then
	/etc/rc.d/init.d/lpd condrestart > /dev/null 2>&1
  fi

%postun pcgi
  if [ $1 = 0 ] ; then
	userdel zope >/dev/null 2>&1 || :
  fi

####
# Section: Verify Script (Check for Proper Installation of Package)
####

%verifyscript zserver
  if [ ! /var/lib/zope/zserver_wo_pcgi.sh -ef /var/lib/zope/zserver.sh ]; then
    echo "/var/lib/zope/zserver_wo_pcgi.sh should be linked to /var/lib/zope/zserver.sh" >&2
  fi

  if [ ! %{_libdir}/zope/import -ef /var/lib/zope/import ]; then
    echo "%{_libdir}/zope/import should be linked to /var/lib/zope/import" >&2
  fi

%verifyscript pcgi
  if [ ! /var/lib/zope/zserver_w_pcgi.sh -ef /var/lib/zope/zserver.sh ]; then
    echo "/var/lib/zope/zserver_w_pcgi.sh should be linked to /var/lib/zope/zserver.sh" >&2
  fi

  if [ ! %{_libdir}/zope/import -ef /var/lib/zope/import ]; then
    echo "%{_libdir}/zope/import should be linked to /var/lib/zope/import" >&2
  fi

####
# Section: Clean Script (Tidy Up Build Area After a Build Completes)
####
%clean
  rm -rf $RPM_BUILD_ROOT

####
# Section: Files (List of Files w/Attributes Making Up Package)
####

# Note: the root package of just Zope (w/o any -<stuff>) includes all
#       of the Zope release, for those who want to quickly install
#       everything.  The release is also packaged as separate subpackages
#       for those who want to be more selective.

%files
  %defattr(-, root, root)

  #-- Copy of Zope-core Contents:
  %doc LICENSE.txt README.txt README.RPM
  %doc ZServer/medusa/medusa/

  # User's Guides
###  %doc /var/www/html/zopedocs/index.html
###  %doc /var/www/html/zopedocs/ZopeContentManagersGuide
###  %doc /var/www/html/zopedocs/GuideToZSQL
###  %doc /var/www/html/zopedocs/Tutorial
###  %doc /var/www/html/zopedocs/ZopeDevelopersGuide
###  %doc /var/www/html/zopedocs/ZopeAdminGuide
  %doc doc/
  %doc lib/python/Products/ZCatalog/ZCatalog.txt
  %doc lib/python/AccessControl/AccessControl.txt
#jrr   %doc misc/pyexpat.README

  # ZOPE-Specific Python Packages
  %{_libdir}/zope/lib/python/

  %{_libdir}/zope/Extensions/
  /usr/bin/zpasswd

  #-- Copy of Zope-components Contents:
  %doc lib/Components/ExtensionClass/ExtensionClass/

  # BTree Module(s):
  %{_libdir}/%{PYTHONDIR}/site-packages/BTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/IIBTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/IOBTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/OIBTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/intSet.so

  # ExtensionClass Module(s):
  %{_libdir}/%{PYTHONDIR}/site-packages/Acquisition.so
  %{_libdir}/%{PYTHONDIR}/site-packages/ComputedAttribute.so
  %{_libdir}/%{PYTHONDIR}/site-packages/ExtensionClass.so
  %{_libdir}/%{PYTHONDIR}/site-packages/MethodObject.so
  %{_libdir}/%{PYTHONDIR}/site-packages/Missing.so
  %{_libdir}/%{PYTHONDIR}/site-packages/MultiMapping.so
  %{_libdir}/%{PYTHONDIR}/site-packages/Record.so
  %{_libdir}/%{PYTHONDIR}/site-packages/Sync.so
  %{_libdir}/%{PYTHONDIR}/site-packages/ThreadLock.so
  %{_libdir}/%{PYTHONDIR}/Xaq.py*
  /usr/include/%{PYTHONDIR}/*.h

  #-- Copy of Zope-zpublisher Contents:
  %{_libdir}/%{PYTHONDIR}/site-packages/ZPublisher/

  #-- Copy of Zope-ztemplates Contents:
  %doc lib/python/DocumentTemplate/Let.stx
###  %doc /var/www/html/zopedocs/GuideToDTML
  %{_libdir}/%{PYTHONDIR}/site-packages/DocumentTemplate/

  #-- Copy of Zope-services Contents:
  %doc lib/python/DateTime/DateTime.html
  %doc lib/python/StructuredText/regressions/
  %{_libdir}/%{PYTHONDIR}/site-packages/DateTime/
  %{_libdir}/%{PYTHONDIR}/site-packages/StructuredText/
  %{_libdir}/%{PYTHONDIR}/site-packages/SearchIndex/
  %{_libdir}/%{PYTHONDIR}/site-packages/BTrees/
  %{_libdir}/%{PYTHONDIR}/site-packages/RestrictedPython/

%files core
  %defattr(-, root, root)
  %doc LICENSE.txt README.txt README.RPM

  # User's Guides
###  %doc /var/www/html/zopedocs/index.html
###  %doc /var/www/html/zopedocs/ZopeContentManagersGuide
###  %doc /var/www/html/zopedocs/GuideToZSQL
###  %doc /var/www/html/zopedocs/Tutorial
###  %doc /var/www/html/zopedocs/ZopeDevelopersGuide
###  %doc /var/www/html/zopedocs/ZopeAdminGuide
###  %doc /var/www/html/zopedocs/ZCatalog.txt
  %doc doc/
  %doc lib/python/AccessControl/AccessControl.txt
#jrr   %doc misc/pyexpat.README

  # ZOPE-Specific Python Packages
  %{_libdir}/zope/lib/python/

  %{_libdir}/zope/Extensions/
  /usr/bin/zpasswd

%files components
  %defattr(-, root, root)
  %doc LICENSE.txt
  %doc lib/Components/ExtensionClass/ExtensionClass/

  # BTree Module(s):
  %{_libdir}/%{PYTHONDIR}/site-packages/BTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/IIBTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/IOBTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/OIBTree.so
  %{_libdir}/%{PYTHONDIR}/site-packages/intSet.so

  # ExtensionClass Module(s):
  %{_libdir}/%{PYTHONDIR}/site-packages/Acquisition.so
  %{_libdir}/%{PYTHONDIR}/site-packages/ComputedAttribute.so
  %{_libdir}/%{PYTHONDIR}/site-packages/ExtensionClass.so
  %{_libdir}/%{PYTHONDIR}/site-packages/MethodObject.so
  %{_libdir}/%{PYTHONDIR}/site-packages/Missing.so
  %{_libdir}/%{PYTHONDIR}/site-packages/MultiMapping.so
  %{_libdir}/%{PYTHONDIR}/site-packages/Record.so
  %{_libdir}/%{PYTHONDIR}/site-packages/Sync.so
  %{_libdir}/%{PYTHONDIR}/site-packages/ThreadLock.so
  %{_libdir}/%{PYTHONDIR}/Xaq.py*
  /usr/include/%{PYTHONDIR}/*.h

%files zpublisher
  %defattr(-, root, root)
  %doc LICENSE.txt
  %{_libdir}/%{PYTHONDIR}/site-packages/ZPublisher/

%files ztemplates
  %defattr(-, root, root)
  %doc LICENSE.txt  lib/python/DocumentTemplate/Let.stx
###  %doc /var/www/html/zopedocs/GuideToDTML
  %{_libdir}/%{PYTHONDIR}/site-packages/DocumentTemplate/

%files services
  %defattr(-, root, root)
  %doc LICENSE.txt  lib/python/DateTime/DateTime.html
  %doc lib/python/StructuredText/regressions/
  %{_libdir}/%{PYTHONDIR}/site-packages/DateTime/
  %{_libdir}/%{PYTHONDIR}/site-packages/StructuredText/
  %{_libdir}/%{PYTHONDIR}/site-packages/SearchIndex/
  %{_libdir}/%{PYTHONDIR}/site-packages/BTrees/
  %{_libdir}/%{PYTHONDIR}/site-packages/RestrictedPython/

%files zserver
  %defattr(-, root, root)
  %doc LICENSE.txt  ZServer/INSTALL.txt  ZServer/README.txt
  %doc ZServer/medusa/medusa/
  %{_libdir}/zope/ZServer/
  %{_libdir}/zope/utilities/
  %{_libdir}/zope/import/

  %config                             /etc/rc.d/init.d/zope
  %config(noreplace) %attr(640, root, zope)      /var/lib/zope/access
  %config                             /var/lib/zope/z2.py
  %config                             /var/lib/zope/zserver_wo_pcgi.sh

  # IMPORTANT: ZServer runs as user 'zope' and
  #            must have r/w access to the var/ directory
  #            so that it can create temp and index files.
  %defattr(-, zope, root)
  %dir                                /var/lib/zope/
  %dir                                /var/lib/zope/Products
  %dir                                /var/lib/zope/var/
                                      /var/lib/zope/Extensions/
  %config(noreplace) %verify(not size md5 mtime) /var/lib/zope/var/Data.fs
  %verify(not size md5 mtime)         /var/log/zope

%files pcgi
  %defattr(-, root, root)
  %doc LICENSE.txt  pcgi/README  ZServer/README.txt  ZServer/INSTALL.txt
  %doc ZServer/medusa/medusa/
  %doc pcgi/Example/  pcgi/Test/  pcgi/Util/

  /usr/bin/pcgi-wrapper
  %{_libdir}/%{PYTHONDIR}/pcgi_publisher.py
  /var/lib/zope/pcgi_nullpublisher.py
  %{_libdir}/%{PYTHONDIR}/killpcgi.py
  %{_libdir}/zope/ZServer/
  %{_libdir}/zope/utilities/
  %{_libdir}/zope/import/

  %config                             /etc/rc.d/init.d/zope
  %config(noreplace) %attr(640, root, zope) /var/lib/zope/access
  %config                             /var/lib/zope/z2.py
  %config                             /var/lib/zope/zserver_w_pcgi.sh
                                      /var/lib/zope/Zope.cgi

  # IMPORTANT: PCGI runs as user 'zope' and must have r/w
  #            access to the var/ directory so that it can
  #            create temp and index files.  ZServer runs as
  #            user 'zope' and must have write access to var.
  %defattr(-, zope, root)
  %dir                                /var/lib/zope/
  %dir                                /var/lib/zope/Products
  %dir                                /var/lib/zope/var/
                                      /var/lib/zope/Extensions
  %config(noreplace) %verify(not size md5 mtime) /var/lib/zope/var/Data.fs
  %verify(not size md5 mtime)         /var/log/zope

%changelog
* Sun Dec 12 2002 Jean-Paul Smets <jp@nexedi.com>
[Release 2.5.1-4nxd]
- Fixed startup scripts

* Sat Oct 12 2002 Jean-Paul Smets <jp@nexedi.com>
[Release 2.5.1-3nxd]
- Added i18 patch to provide simple implementation of i18n
  features based on Localizer and gettext

* Fri Oct 04 2002 Jean-Paul Smets <jp@nexedi.com>
[Release 2.5.1-2nxd]
- Rebuilt 2.5.1 with Mandrake 9.0.

* Tue Aug 06 2002 Jean-Paul Smets <jp@nexedi>
  Changed /usr/share/zope to %{_libdir}/zope for Debian Zope compatibility
  Compiled on Mandrake 9.0 Beta

* Sat Jun 22 2002 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.5.1 and removed html docs (latest on zope.org)

* Wed Nov 14 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.4.3.

* Sat Nov 10 2001 Jeff Rush <jrush@taupro.com>
  changed args to useradd, to work with Red Hat 7.2.

* Sun Oct 21 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.4.2, removed Hotfix 2001-09-28.

* Thu Oct 18 2001 Jeff Rush <jrush@taupro.com>
  Fixed broken syslogging facility and added Hotfix 2001-09-28.

* Mon Sep 04 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.4.1, removed Hotfix 2001-08-04.

* Mon Aug 15 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.4.0, changed to use python2.1, added Hotfix 2001-08-04.

  Merged in Jun 29 2001 patch from Durval Menezes re support for ZPatterns:
  "No longer removes cPersistence.h from lib/python/ZODB before installing
  (this is needed to compile DynPersist, as part of the ZPatterns
  installation.  Installs ExtensionClass.h into /usr/include/python2.1
  (it too is needed to compile DynPersist, as part of the ZPatterns install)"

  Merged in Jun 12 2001 additions from Jared Kelsey <jared@dolphinsearch.com>
  to make more compatible with future releases of python.

* Mon Aug 14 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.3.3, added Hotfix 2001-08-04.

* Mon May 07 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.3.2, added Hotfix 2001-05-01, revised access
  file permissions (600->640) and ownership (root.root->root.zope)
  to fix the "can't log in" bug under ZServer subpackage.

* Sat Mar 31 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.3.1

* Mon Jan 29 2001 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.3.0; removed obsolete Hotfixes.

* Fri Dec 08 2000 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.2.4; removed obsolete Hotfixes.

* Fri Nov 03 2000 Jeff Rush <jrush@taupro.com>
  fixed misplaced SiteAccess, where dirs in tar moved btw v1 and v2.

* Sun Oct 16 2000 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.2.2; added Hotfixes  2000-10-02 and 2000-10-11.

* Sun Aug 27 2000 Jeff Rush <jrush@taupro.com>
  bumped to zope 2.2.1; removed no-longer-needed Hotfix_2000-08-17

* Tue Aug 22 2000 Jeff Rush <jrush@taupro.com>
- added Hotfix_2000-08-17
- temporarily removed /etc/init.d (RH7.0) until I figure out how
  to support both RH6.x *and* RH7.0 in the same RPM. <sigh>
- removed troublesome/obsolete ComputedAttribute.py

* Sun Jul 16 2000 Jeff Rush <jrush@taupro.com>
- bumped to zope 2.2.0; removed no-longer-needed Hotfix-06_16_2000

* Thu Jul 06 2000 Tim Powers <timp@redhat.com>
- fixed PreReq to PreReq /etc/init.d
- added Hotfix-06_16_2000
 
* Thu Jun 15 2000 Preston Brown <pbrown@redhat.com>
- moved init script, added condrestart directive
- auto stop/restart service on upgrades

* Thu Jun 1 2000 Tim Powers <timp@redhat.com>
- fixed so that it's no longer putting files into /home, instead they are
  going into /var/www (FHS compliant).

* Mon May 22 2000 Tim Powers <timp@redhat.com>
- built for 7.0, thanks Jeff!

* Fri Apr 28 2000 Jeff Rush <jrush@taupro.com>
- bumped to zope 2.1.6

* Sun Mar 12 2000 Jeff Rush <jrush@taupro.com>
- added zpasswd.py back in, since my rename to just zpasswd confused some.
  both are now present in the RPM, for all audiences.
- modified the README.RPM re the section about Apache rewrite rules; I
  discussed and removed the trailing slash, the presence of which causes
  Zope to reject attempts to delete objects in the root folder.

* Thu Feb 26 2000 Jeff Rush <jrush@taupro.com>
- 2.1.4-1 Release on Zope.org site
- bumped to zope 2.1.4
- changed Zope-core to provide 'Zope', to satisfy zserver and pcgi subpkgs.

* Fri Jan 14 2000 Tim Powers <timp@redhat.com>
- added Provides lines to Zope-pcgi and Zope-zserver so that addon packages
	such as Squishdot have something useful to require.

* Thu Jan 13 2000 Tim Powers <timp@redhat.com>
- built for Powertools 6.2

* Thu Jan 11 2000 Jeff Rush <jrush@taupro.com>
- bumped to zope 2.1.2
- folded in Jonathan Marsden <jonathan@xc.org> Changes (many below)
- used zpasswd.py to generate initial pw in encrypted form.
- fixed syslog logging in various ways, and re-enabled it, for both
-    ZServer AND pcgi-wrapper.
- fixed /etc/rc.d/init.d/zope to be consistent about pid file.
- fixed /etc/rc.d/init.d/zope to use RH killproc function.
- added 'noreplace' so that Zope database and access file are retained
-    on an RPM upgrade.
- patched PCGI to support syslog logging, and then default to it.
- patched ZServer/Medusa to properly support syslog logging.
- added a user 'zope' and made many zope files/dirs owned by it.
- cleaned up pcgi-wrapper's msg about can't find ZServer, since it is
-    one of the most common errors.  It now explains what it is doing.
- moved all *.{pid,soc} files into /var/run, to cleanly separate ownership
-    issues in /var/lib/zope hierarchy for user 'zope' and user 'nobody'.

* Mon Jan 03 2000 Jeff Rush <jrush@taupro.com>
- bumped to zope 2.1.1
- added to /etc/rc.d/init.d/zope code to correctly kill the process specified
-    in /var/lib/zope/pcgi.pid
- changed permissions on /var/lib/zope/access such that only root can read/write
-    it, to protect the Zope superuser password.

* Sat Nov 29 1999 Jeff Rush <jrush@taupro.com>
- changed ownership on /var/lib/zope/access from nobody.nobody to root.root.

* Sat Nov 20 1999 Jeff Rush <jrush@taupro.com>
- updated to zope 2.1.0beta2
- fixed permissions/ownership on /var/lib/zope/access to be more secure (600).
- removed pypath.patch, as those changes got into the zope distribution.

* Tue Nov 2 1999 Jeff Rush <jrush@taupro.com>
- added accidentally omitted /usr/bin/zpasswd to the RPM output.
- clarified wording re use of zpasswd in README.RPM file.
- added "-u nobody" to both zserver_*.sh files, for clarity of intent;
-    it already ran as nobody by default, but some people worried.

* Wed Oct 27 1999 Jeff Rush <jrush@taupro.com>
- fixed /etc/rc.d/init.d/zope file to *NOT* delete /var/lib/zope/zserver.pid
- fixed /var/lib/zope/Zope.cgi to use PCGI_PUBLISHER=/var/lib/zope/pcgi_nullpublisher.py,
-    so that when the PCGI wrapper can't find ZServer, it won't try to start one
-    and generate bogus error messages, because PCGI doesn't do it right.
- fixed /var/lib/zope/zserver.sh to NOT specify syslog-style logging, since under
-    Red Hat 6.1, the syslog daemon no longer listens to the port we expected.

* Sat Sep 25 1999 Jeff Rush <jrush@taupro.com>
- updated documents ZCMG, ZSQL and ZDTML to Sep 24th 1999 versions
- added empty directories /var/lib/zope/{import,Extensions}
- relocated zope from %{_libdir}/python1.5/site-packages/ZopeWorld/
-    to %{_libdir}/zope/
- added user zope, for better security control

* Fri Sep 17 1999 Jeff Rush <jrush@taupro.com>
- updated sources to minor (security fix) release 2.0.1

* Fri Sep 10 1999 Jeff Rush <jrush@taupro.com>
- heavily reworked spec file for 2.0.0

* Thu Sep 9 1999 Tim Powers <timp@redhat.com>
- updated sources to 2.0.0
- _major_ spec file cleanups
- merged patch from src.rpm authored by Andreas Kostyrka <andreas@mtg.co.at>
- borrowed some things from Andreas Kostyrka's spec file

* Mon Aug 30 1999 Tim Powers <timp@redhat.com>
- changed groups

* Tue Aug 17 1999 Tim Powers <timp@redhat.com>
- chown permissions on some files in /var/local for the pcgi package

* Mon Aug 2 1999 Tim Powers <timp@redhat.com>
- changed buildroot to be in %{_tmppath} instead of /tmp
- rebuilt for 6.1

* Mon Jul 21 1999 Jeff Rush <jrush@taupro.com>
- Added in accidently omitted SearchIndex/{Query,Splitter}.so

* Tue Jul 6 1999 Tim Powers <timp@redhat.com>
- started changelog
- cleaned up spec file
- built for powertools

* Mon Jun 24 1999 Jeff Rush <jrush@taupro.com>
- Updated to 1.10.3

* Mon Jun 23 1999 Jeff Rush <jrush@taupro.com>
- Added /etc/rc.d/init.d/zope and reworked scripts

* Tue Mar 1 1999 Jeff Rush <jrush@taupro.com>
- Updated to 1.10.2

* Wed Jan 29 1999 Jeff Rush <jrush@taupro.com>
- Updated to 1.9.0 Final Release

* Wed Dec 9 1998 Jeff Rush <jrush@taupro.com>
- Original 1.9beta1 Release

