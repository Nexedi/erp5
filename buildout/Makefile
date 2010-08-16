PYTHON=python
SOFTWARE_BUILD_PATH='/opt/erp5/'`cat VERSION.txt`
PACKAGE_INSTALL_PATH='opt/erp5/'`cat VERSION.txt`
ifndef $(PACKAGE_VERSION)
PACKAGE_VERSION=`cat VERSION.txt`
endif
ifndef $(PACKAGE_SOFTWARE_RELEASE)
PACKAGE_SOFTWARE_RELEASE=001
endif
ifndef $(PACKAGE_APPLICATION_RELEASE)
PACKAGE_APPLICATION_RELEASE=001
endif

software: bin/buildout
	bin/buildout

bin/buildout:
	$(PYTHON) -S bootstrap/bootstrap.py

# run make assert to check that all is working
assert: bin/python2.4
	bin/python2.4 tests/assertSoftware.py

debian-appliance:
	svn co --ignore-externals https://svn.erp5.org/repos/public/spec/debian-erp5-appliance/ debian-erp5-appliance
	sed -i "s,__PACKAGE_NAME__,erp5-$(PACKAGE_VERSION),g" debian-erp5-appliance/debian/control
	sed -i "s,__PACKAGE_VERSION__,$(PACKAGE_VERSION),g" debian-erp5-appliance/debian/changelog
	sed -i "s,__PACKAGE_RELEASE__,$(PACKAGE_SOFTWARE_RELEASE),g" debian-erp5-appliance/debian/changelog
	sudo svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout $(SOFTWARE_BUILD_PATH)
	sudo chown -R `whoami` $(SOFTWARE_BUILD_PATH)
	sudo $(SOFTWARE_BUILD_PATH)/helpers/debian.lenny.sh
	cd $(SOFTWARE_BUILD_PATH); $(MAKE) $(MFLAGS)
	mkdir -p debian-erp5-appliance/debian/erp5-$(PACKAGE_VERSION)/$(PACKAGE_INSTALL_PATH)
	mv $(SOFTWARE_BUILD_PATH)/* debian-erp5-appliance/debian/erp5-$(PACKAGE_VERSION)/$(PACKAGE_INSTALL_PATH)
	find debian-erp5-appliance/debian/erp5-$(PACKAGE_VERSION)/$(PACKAGE_INSTALL_PATH) -type d -name .svn -exec rm -rf {} \;
	find debian-erp5-appliance/debian/erp5-$(PACKAGE_VERSION)/$(PACKAGE_INSTALL_PATH) -name '*.pyc' -delete
	rm -rf debian-erp5-appliance/debian/erp5-$(PACKAGE_VERSION)/$(PACKAGE_INSTALL_PATH)/downloads/* 
	rm -rf debian-erp5-appliance/debian/erp5-$(PACKAGE_VERSION)/$(PACKAGE_INSTALL_PATH)/parts/*__unpack__
	cd debian-erp5-appliance/; sudo dpkg-buildpackage -b 
	svn co  https://svn.erp5.org/repos/public/spec/debian-tiolive-application/ debian-tiolive-application
	sed -i "s,__PACKAGE_VERSION__,$(PACKAGE_VERSION),g" debian-tiolive-application/debian/rules
	sed -i "s,__PACKAGE_VERSION__,$(PACKAGE_VERSION),g" debian-tiolive-application/debian/changelog
	sed -i "s,__PACKAGE_RELEASE__,$(PACKAGE_SOFTWARE_RELEASE),g" debian-tiolive-application/debian/changelog
	cd debian-tiolive-application; sudo dpkg-buildpackage -b

checkout-rpmgen:
	svn co https://svn.erp5.org/repos/public/erp5/trunk/utils/rpmgen rpmgen

mandriva-rpm-appliance: checkout-rpmgen
	sed -i "s,name = erp5-official-buildout,name = erp5-`cat VERSION.txt`,g" rpmgen/profiles/mandriva.cfg
	sed -i "s,\$${checkout:location\}\/VERSION.txt,$(PACKAGE_VERSION),g" rpmgen/profiles/mandriva.cfg
	sed -i "/release \= 001/{x;/^$$/s//0/;y/012/123/;/2/{x;s/release = 001/release = $(PACKAGE_APPLICATION_RELEASE)/;x;};x;}" rpmgen/profiles/mandriva.cfg
	sed -i 's,release = 001,release = $(PACKAGE_SOFTWARE_RELEASE),1' rpmgen/profiles/mandriva.cfg
	sed -i "s,\$$(shell cat parts/checkout/VERSION.txt), `cat VERSION.txt`,g" rpmgen/Makefile
	sudo helpers/mandriva2010.0.sh
	cd rpmgen; make mandriva

opensuse11.2-rpm-appliance: checkout-rpmgen
	sed -i "s,mandriva,opensuse11.2,g" rpmgen/buildout.cfg
	sed -i "s,name = erp5-official-buildout,name = erp5-$(PACKAGE_VERSION),g" rpmgen/profiles/opensuse11.2.cfg
	sed -i "s,\$${checkout:location\}\/VERSION.txt,$(PACKAGE_VERSION),g" rpmgen/profiles/opensuse11.2.cfg
	sed -i "/release \= 001/{x;/^$$/s//0/;y/012/123/;/2/{x;s/release = 001/release = $(PACKAGE_APPLICATION_RELEASE)/;x;};x;}" rpmgen/profiles/opensuse11.2.cfg
	sed -i 's,release = 001,release = $(PACKAGE_SOFTWARE_RELEASE),1' rpmgen/profiles/opensuse11.2.cfg
	sed -i "s,\$$(shell cat parts/checkout/VERSION.txt),$(PACKAGE_VERSION),g" rpmgen/Makefile
	sudo helpers/opensuse.sh
	cd rpmgen; make opensuse

opensuse11.3-rpm-appliance: checkout-rpmgen
	sed -i "s,mandriva,opensuse11.3,g" rpmgen/buildout.cfg
	sed -i "s,name = erp5-official-buildout,name = erp5-$(PACKAGE_VERSION),g" rpmgen/profiles/opensuse11.3.cfg
	sed -i "s,\$${checkout:location\}\/VERSION.txt,$(PACKAGE_VERSION),g" rpmgen/profiles/opensuse11.3.cfg
	sed -i "/release \= 001/{x;/^$$/s//0/;y/012/123/;/2/{x;s/release = 001/release = $(PACKAGE_APPLICATION_RELEASE)/;x;};x;}" rpmgen/profiles/opensuse11.3.cfg
	sed -i 's,release = 001,release = $(PACKAGE_SOFTWARE_RELEASE),1' rpmgen/profiles/opensuse11.3.cfg
	sed -i "s,\$$(shell cat parts/checkout/VERSION.txt),$(PACKAGE_VERSION),g" rpmgen/Makefile
	sudo helpers/opensuse.sh
	cd rpmgen; make opensuse

fedora12-rpm-appliance: checkout-rpmgen
	sed -i "s,mandriva,fedora12,g" rpmgen/buildout.cfg
	sed -i "s,name = erp5-official-buildout,name = erp5-$(PACKAGE_VERSION),g" rpmgen/profiles/fedora12.cfg
	sed -i "s,\$${checkout:location\}\/VERSION.txt,$(PACKAGE_VERSION),g" rpmgen/profiles/fedora12.cfg
	sed -i "/release \= 001/{x;/^$$/s//0/;y/012/123/;/2/{x;s/release = 001/release = $(PACKAGE_APPLICATION_RELEASE)/;x;};x;}" rpmgen/profiles/fedora12.cfg
	sed -i 's,release = 001,release = $(PACKAGE_SOFTWARE_RELEASE),1' rpmgen/profiles/fedora12.cfg
	sed -i "s,\$$(shell cat parts/checkout/VERSION.txt),$(PACKAGE_VERSION),g" rpmgen/Makefile
	sudo helpers/fedora.sh
	cd rpmgen; make fedora

fedora13-rpm-appliance: checkout-rpmgen
	sed -i "s,mandriva,fedora13,g" rpmgen/buildout.cfg
	sed -i "s,name = erp5-official-buildout,name = erp5-$(PACKAGE_VERSION),g" rpmgen/profiles/fedora13.cfg
	sed -i "s,\$${checkout:location\}\/VERSION.txt,$(PACKAGE_VERSION),g" rpmgen/profiles/fedora13.cfg
	sed -i "/release \= 001/{x;/^$$/s//0/;y/012/123/;/2/{x;s/release = 001/release = $(PACKAGE_APPLICATION_RELEASE)/;x;};x;}" rpmgen/profiles/fedora13.cfg
	sed -i 's,release = 001,release = $(PACKAGE_SOFTWARE_RELEASE),1' rpmgen/profiles/fedora13.cfg
	sed -i "s,\$$(shell cat parts/checkout/VERSION.txt),$(PACKAGE_VERSION),g" rpmgen/Makefile
	sudo helpers/fedora.sh
	cd rpmgen; make fedora

