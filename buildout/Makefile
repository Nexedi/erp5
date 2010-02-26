INSTALL_PATH='opt/erp5/'`cat VERSION.txt`

software: bin/buildout
	bin/buildout

bin/buildout:
	python bootstrap/bootstrap.py

# run make assert to check that all is working
assert: bin/python2.4
	bin/python2.4 tests/assertSoftware.py

debian-appliance:
	svn co https://svn.erp5.org/repos/public/spec/debian-erp5-appliance/ debian-erp5-appliance
	cd debian-erp5-appliance/$(INSTALL_PATH); $(MAKE) $(MFLAGS)
	rm -rf debian-erp5-appliance/*.txt
	rm -rf `find . -type d -name .svn`
	rm -rf `find . -name *.pyc`
	cd ../../../../
	dpkg-deb -b debian-erp5-appliance/ .
