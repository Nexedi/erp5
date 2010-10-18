Debian ERP5 Appliance
---------------------
As ERP5 Appliance is not relocatable itself yet, building packages
requires to build them in same structure like they would be installed.
So to have /opt/erp5/9.9.9 build have to be done in such directory. This
is known limitation and affects both builds - RPM and DEB.

How to build debian package
---------------------------
Checkout: https://svn.erp5.org/repos/public/erp5/trunk/buildout

For example:
  svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout ~/buildout

Run make inside:
  cd ~/buildout
  make -f Makefile.packages debian-appliance PACKAGE_VERSION=001

