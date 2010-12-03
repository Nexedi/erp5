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

Software part is system independent.

Requirements to build ERP5 Appliance 2.12 are:

 * C and C++ compiler (gcc and g++)
 * standard C and C++ library with development headers (glibc and libstdc++)
 * make
 * patch
 * python (>=2.4) with development headers (to run buildout)

** WARNING ** DO __NOT__ use helpers, they are only for ERP5 Appliance 2.8 flavour. ** WARNING **

Setup
-----

Create directory for buildout and its extends cache:

  $ mkdir -p ~/erp5.buildout/{downloads,extends-cache}

Go to this directory:

  $ cd ~/erp5.buildout

Create buildout.cfg there:

  $ cat > buildout.cfg

[buildout]
extends = https://svn.erp5.org/repos/public/erp5/trunk/buildout/buildout-2.12.cfg
extends-cache = extends-cache
^D

Bootstrap buildout
~~~~~~~~~~~~~~~~~~

WARNING: please read "Troubleshooting" section bellow, you may need to
unset environment variables in your GNU/Linux distribution

  $ python -S -c 'import urllib2;print urllib2.urlopen("http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py").read()' | python -S -

Run the buildout
~~~~~~~~~~~~~~~~

  $ bin/buildout -v

This will download and install the software components needed to run ERP5 on
Zope 2.12 including Zope 2.12 plus dependencies (including
Acquisition with _aq_dynamic patch) and CMF 2.2 plus dependencies.

Note on -S: this switch is overridden by PYTHON_PATH environment variable. In
doubt, unset it before invoking that command.

Post-build check
----------------

There are tests for buildout in:
  https://svn.erp5.org/repos/public/erp5/trunk/buildout/tests/assertSoftware.py

Download this file, for example by using provided svn:

 $ parts/subversion/bin/svn export --non-interactive --trust-server-cert https://svn.erp5.org/repos/public/erp5/trunk/buildout/tests/assertSoftware.py
Run:
  python assertSoftware.py

Instances
=========

Note: Instance generation is still a work in progress. In particular, these
instructions should be much simplified.

After the software components are built, we can generate ERP5 instance
buildouts from that software.

Assuming the ERP5 software buildout is available in ~/erp5.buildout the
following sequence of steps should result in a working "instance" buildout:

$ mkdir ~/instances                         # 0
$ cd ~/instances                            # 1
$ cat > buildout.cfg                        # 3

[buildout]
# Reuse extends from software
extends-cache = ~/erp5.buildout/extends-cache
# Default run buildout in offline mode.
offline = true
extends =
  https://svn.erp5.org/repos/public/erp5/trunk/buildout/profiles/development-2.12.cfg
  ~/erp5.buildout/instance.inc

parts =
  mysql-instance
  oood-instance
  supervisor-instance
^D

$ ~/erp5.buildout/bin/bootstrap2.6      # 4
$ bin/buildout -v         # 5

The software-home configuration (along with the 'extends-cache' in the
'instance-profiles' symlink) provides all the information and components that
would otherwise have to be downloaded.

The steps above generate instance configurations for mysql and the
OpenOffice.org document conversion daemon. We need mysql, in particular,
to be running before configuring an actual ERP5 instance, so we'll start
supervisor:

$ bin/supervisord                   # 6

Now it is time to give supervisor few moments (about 10 seconds) to start all
required services. By running bin/supervisorctl status one can be informed if mysql
and oood are running.

Also, we need databases in the mysql server that correspond to both the ERP5
instance we're going to create, and the testrunner we will want to run:

$ var/bin/mysql -h 127.0.0.1 -u root
mysql> create database development_site;
mysql> grant all privileges on development_site.* to 'development_user'@'localhost' identified by 'development_password';
mysql> grant all privileges on development_site.* to 'development_user'@'127.0.0.1' identified by 'development_password';
mysql> create database test212;
mysql> grant all privileges on test212.* to 'test'@'localhost';
mysql> grant all privileges on test212.* to 'test'@'127.0.0.1';
mysql> exit

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
'profiles/development-2.12.cfg'. The file 'instance-profiles/zope-2.12.cfg'
provides the "Manager" credentials you should use (usually zope:zope), in
the 'zope-instance-template:user' variable.

You should also be able to run ERP5 unit tests like so:

 $ bin/runUnitTest testClassTool

Troubleshooting
===============

In various Linux distributions python is heavily patched and user related
environment variables are set system wide. This affects behaviour of python
and introduces various problem with running buildout.

In case of such issues consider resetting some python environment variables
before running buildout:

 * PYTHONPATH
 * PYTHONSTARTUP
 * PYTHONDONTWRITEBYTECODE

Example:

$ unset PYTHONPATH PYTHONSTARTUP PYTHONDONTWRITEBYTECODE
$ make
$ # other buildout related commands

TODO
====

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
