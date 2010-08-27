=============
ERP5 buildout
=============

Introduction
============

ERP5 Buildout is providing a way to build and manage ERP5 software components
with all needed dependencies.

ERP5 Buildout is also providing a way to manage instances of software
(whenever provided by ERP5 Buildout or externally).


Software
========

Software part shall be system independent. In perfect world it shall depend
only on:

 * C compiler
 * standard C and C++ library
 * operating system kernel

As world is not perfect some additional build time requirements are added,
please look below for a way to acquire list of dependencies and system helpers.

How to run
----------

Checkout: https://svn.erp5.org/repos/public/erp5/trunk/buildout/
For example:

  svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout/ ~/erp5.buildout

Run make inside:

  cd ~/erp5.buildout
  make

It will install required software and configure it locally, up to ERP5 site
with some Business Templates. By default it will use local python, MySQL,
Zope, etc.

Choosing and modifying proper profile allows to control how much software will
be build in place.

Minimal requirements
--------------------

To start buildout it is required to have:

 * any python with header files (file similar to
   /usr/lib*/python*/config/Makefile have to be delivered by system package)
 * svn client (to checkout buildout)

After build check
-----------------

After software is build invoke:

  make assert

To be sure that all components are available (corretly build and linked).

Distribution helpers
--------------------

In profiles directory there are profiles to help with preparation of used
distributions.

To prepare Mandriva 2010.0 please type, having root privileges:

  helpers/mandriva2010.0.sh

There are more helpers available, please refer to helpers directory.

Instances
=========

Note: Instance generation is still work in progress.

After software is generated it is time to have instances running.
The easiest way to generate instance is of course to reuse generated software.
If software is available in ~/erp5.buildout, such scenario work:

$ svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout/ ~/instances
$ cd instances
$ cat > my_instances.cfg
[buildout]
extends = profiles/development.cfg

parts =
  software-links
  mysql-instance
  oood-instance
  supervisor-instance

[software_definition]
software_home = /home/MYUSER/erp5.buildout
^D
$ ~/erp5.buildout/bin/python2.4 bootstrap/bootstrap.py -c my_instances.cfg
$ python -S bin/buildout -c my_instances.cfg
$ var/bin/supervisord # it will start supervisor and configured software
$ $EDITOR my_instances.cfg
# add "runUnitTest" and "development-site" to parts
$ python -S bin/buildout -c my_instances.cfg

Fully configured development instance will be available in var/development-site.

Network based invocation
========================

Buildout profile can extend other ones from network. It is possible to play
with ERP5 buildout that way.

What to do:

$ mkdir software
$ cd software
$ echo '[buildout]' >> buildout.cfg
$ echo 'extends = https://svn.erp5.org/repos/public/erp5/trunk/buildout/buildout.cfg' >> buildout.cfg
$ wget -qO - http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py | python -S - -d
$ python -S bin/buildout

Note on -S: this switch is overridden by PYTHON_PATH environment variable. In
doubt, unset it before invoking that command.

After some time everything shall be locally available.

Disclaimer: That way is still in early stage of development.
