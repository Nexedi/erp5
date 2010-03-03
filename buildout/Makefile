SOFTWARE_BUILD_PATH='/opt/erp5/'`cat VERSION.txt`
PACKAGE_INSTALL_PATH='opt/erp5/'`cat VERSION.txt`
ifndef $(PACKAGE_VERSION)
PACKAGE_VERSION=`cat VERSION.txt`
endif

software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: bin/python2.4
	bin/python2.4 tests/assertSoftware.py

debian-appliance:
	svn co --ignore-externals https://svn.erp5.org/repos/public/spec/debian-erp5-appliance/ debian-erp5-appliance
	sed -i "s,__VERSION__,$(PACKAGE_VERSION),g" debian-erp5-appliance/DEBIAN/control
	sed -i "s,__VERSION__,`cat VERSION.txt`,g" debian-erp5-appliance/DEBIAN/prerm
	svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout $(SOFTWARE_BUILD_PATH)
	cd $(SOFTWARE_BUILD_PATH); #$(MAKE) $(MFLAGS)
	mkdir -p debian-erp5-appliance/$(PACKAGE_INSTALL_PATH)
	mv $(SOFTWARE_BUILD_PATH)/* debian-erp5-appliance/$(PACKAGE_INSTALL_PATH)
	rm -rf debian-erp5-appliance/*.txt
	rm -rf debian-erp5-appliance/*.TXT
	rm -rf `find debian-erp5-appliance/ -type d -name .svn`
	rm -rf `find debian-erp5-appliance/ -name *.pyc`
	dpkg-deb -b debian-erp5-appliance/ erp5-`cat VERSION.txt`.deb

