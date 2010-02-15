ERP5 buildout
=============

This is ERP5 buildout. It contains all software components required to build
and run ERP5 on operating system, which provides compiler, some widespread used
binaries and development files (headers and libraries).

How to run
----------

Checkout: https://svn.erp5.org/repos/public/erp5/trunk/buildout/
Bootstrap: python bootstrap/bootstrap.py
Run buildout: bin/buildout

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

