SOFTWARE_BUILD_PATH='/opt/erp5/'`cat VERSION.txt`
PACKAGE_INSTALL_PATH='opt/erp5/'`cat VERSION.txt`

software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: bin/python2.4
	bin/python2.4 tests/assertSoftware.py

debian-appliance:
	svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout $(SOFTWARE_BUILD_PATH)
	cd $(SOFTWARE_BUILD_PATH); $(MAKE) $(MFLAGS)
	svn co --ignore-externals https://svn.erp5.org/repos/public/spec/debian-erp5-appliance/ debian-erp5-appliance
	mkdir -p debian-erp5-appliance/$(PACKAGE_INSTALL_PATH)
	mv $(SOFTWARE_BUILD_PATH)/* debian-erp5-appliance/$(PACKAGE_INSTALL_PATH)
	rm -rf debian-erp5-appliance/*.txt
	rm -rf debian-erp5-appliance/*.TXT
	rm -rf `find debian-erp5-appliance/ -type d -name .svn`
	rm -rf `find debian-erp5-appliance/ -name *.pyc`
	dpkg-deb -b debian-erp5-appliance/ .

