===========================
ERP5 buildout for Zope 2.12
===========================

Introduction
============

ERP5 Buildout provides a way to build and manage ERP5 software components
with all needed dependencies.

ERP5 Buildout also provides a way to manage separate installation instances of
ERP5 to share non-data components of an ERP5 software installation from a
single location, allowing for easy component upgrade.

Software
========

Software part shall be system independent. In perfect world it shall depend
only on:

 * C compiler
 * standard C and C++ library
 * operating system kernel

As the world is not yet perfect, some additional build time requirements are
needed. See below for a way to acquire the list of system dependencies through
helpers.

Setup
-----

Checkout: https://svn.erp5.org/repos/public/erp5/trunk/buildout/
For example:

  svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout/ ~/erp5.buildout

Run the Zope 2.12 buildout:

  $ cd ~/erp5.buildout
  $ python2.6 -S bootstrap/bootstrap.py -d -v buildout-2.12.cfg
  $ bin/buildout -v -c buildout-2.12.cfg

This will download and install the software components needed to run ERP5 on
Zope 2.12 including Zope 2.12 plus dependencies (including
Acquisition with _aq_dynamic patch) and CMF 2.2 plus dependencies.

Note on -S: this switch is overridden by PYTHON_PATH environment variable. In
doubt, unset it before invoking that command.

System dependency check
-----------------------

Each software component in this buildout might require some system
dependencies, including development libraries and executables.
To query what is required for all components, please run:

  $ bin/buildout install show-requirements

Minimal requirements
--------------------

At the very least, running buildout requires:

 * Python 2.4 or later including development files (e.g. python2.4-devel or 
   python2.4-dev package from your system package manager. A file like
   /usr/lib*/python*/config/Makefile should be installed in the system.
   XXX Since we compile our own python, are development files still necessary?)
 * C development toolchain (Make, gcc, gpp, etc.) 
 * subversion (svn) client, to check-out this buildout.

Post-build check
----------------

There isn't yet a post-build check for running ERP5 on Zope 2.12.

Distribution helpers
--------------------

In the 'helpers' directory there are shell scripts to prepare different
GNU/Linux distributions to run this buildout.

For instance, to prepare Mandriva 2010.0 please type the following with root
privileges:

  helpers/mandriva2010.0.sh

Please refer to the 'helpers' directory for other distributions.

Instances
=========

Note: Instance generation is still a work in progress. In particular, these
instructions should be much simplified.

After the software components are built, we can generate ERP5 instance
buildouts from that software.

Assuming the ERP5 software buildout is available in ~/erp5.buildout the
following sequence of steps should result in a working "instance" buildout:

$ mkdir ~/instances                     # 0
$ cd ~/instances                        # 1
$ ln -s ~/erp5.buildout/*profiles* .    # 2
$ cat > buildout.cfg                    # 3

[buildout]
extends-cache = instance-profiles/extends-cache
extends =
  profiles/development-2.12.cfg
  instance-profiles/software-home.inc

parts =
  mysql-instance
  oood-instance
  supervisor-instance
^D
$ ~/erp5.buildout/bin/bootstrap2.6      # 4
$ bin/buildout -ov         # 5

Notice how we managed to run buildout in "offline-mode" (-o). The software-home
configuration (along with the 'extends-cache' in the 'instance-profiles'
symlink) provides all the information and components that would otherwise have
to be downloaded.

The steps above generate instance configurations for mysql and the
OpenOffice.org document conversion daemon. We need mysql, in particular,
to be running before configuring an actual ERP5 instance, so we'll start
supervisor:

$ bin/supervisord                   # 6

Also, we need databases in the mysql server that correspond to both the ERP5
instance we're going to create, and the testrunner we will want to run:

$ var/bin/mysql -u root
mysql> create database development_site;
mysql> grant all privileges on development_site.* to 'development_user'@'localhost' identified by 'development_password';
mysql> grant all privileges on development_site.* to 'development_user'@'127.0.0.1' identified by 'development_password';
mysql> create database test212
mysql> grant all privileges on test212.* to 'test'@'localhost';
mysql> grant all privileges on test212.* to 'test'@'127.0.0.1';

(there is automated support for creating databases but it's not currently
working with the Zope 2.12 buildout)

$ var/bin/

Now edit buildout.cfg and add "runUnitTest" (w/o quotes) to 'buildout:parts'.
The "development-instance" part will be pulled in automatically as a
dependency:

$ $EDITOR buildout.cfg                  # 7

Then run buildout again to finish the configuration

$ bin/buildout -ov         # 8

Now a fully configured development instance will be available in the directory
"var/development-instance", so you can do:

 $ var/development-site/bin/zopectl fg

And see an ERP5 instance running on "http://localhost:18080/". The port '18080'
refers to the 'development-instance:http-address' setting in
'instance-profiles/development-2.12.cfg'. The file 
'instance-profiles/zope-2.12.cfg' provides the "Manager" credentials you should
use (usually zope:zope), in the 'zope-instance-template:user' variable.

You should also be able to run ERP5 unit tests like so:

 $ bin/runUnitTest --erp5_sql_connection_string="test@127.0.0.1:10002 test" testBusinessTemplate

The '127.0.0.1:10002' coordinate above refers to the address of the configured
mysql instance, according to the settings 'configuration:mysql_host' and
'configuration:mysql_port' in 'instance-profiles/mysql.cfg'.

TODO
====

 * Adjust the 'runUnitTest' recipe to push the mysql server coordinates into
   the 'bin/runUnitTest' script.

 * Refactor the .cfg files to reduce duplication and so that only the
   'instance-profiles' directory needs to be symlinked. Alternatively, push all
   .cfg files into a single 'profiles'
   directory.

 * Combine steps 2, 3 and 4 into a single step by creating a more powerful
   'bootstrap2.6' script.

 * Running 'buildout' twice in the instance (once to configure 'supervisor',
   'mysql' and 'oood' and once to setup the ZODB ERP5 instance) is confusing
   and error-prone. A buildout shouldn't deal with persistent state, only with
   file installation. Move the mysql database and ERP5 ZODB instance creation
   procedures to dedicated scripts in 'bin/' instead of implicitly running them
   in the (second) buildout run.

 * Patch the SOAPpy package provided by Nexedi so it doesn't fail with a
   SyntaxError on Python 2.6. Right now we're using a SOAPpy repackaging from
   http://ibid.omnia.za.net/eggs/ .

 * Synchronize the buildout behaviour for Zope 2.8 and 2.12 (i.e. allows Zope
   2.8 to work with a single buildout check-out).

 * See if we can use http://pypi.python.org/pypi/zc.sourcerelease/ to generate
   a single (humongous) tarball with all needed software components for fully
   offline operation.

 * Figure out why garbage is left on <software_home>/parts/unit_test after the
   test run. It can influence later test runs.
