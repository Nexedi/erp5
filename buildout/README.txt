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

System dependency check
-----------------------

As each software component this buildout requires something to be installed.
To query what is required please use:

bin/buildout install show-requirements

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
