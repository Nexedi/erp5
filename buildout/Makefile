SOFTWARE_BUILD_PATH='/opt/erp5/'`cat VERSION.txt`
PACKAGE_INSTALL_PATH='opt/erp5/'`cat VERSION.txt`
ifndef $(PACKAGE_VERSION)
PACKAGE_VERSION=`cat VERSION.txt`
endif
ifndef $(PACKAGE_RELEASE)
PACKAGE_RELEASE="None"
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
	sed -i "s,__PACKAGE_NAME__,erp5-`cat VERSION.txt`,g" debian-erp5-appliance/DEBIAN/control
	sed -i "s,__VERSION__,$(PACKAGE_VERSION),g" debian-erp5-appliance/DEBIAN/control
	sed -i "s,__VERSION__,`cat VERSION.txt`,g" debian-erp5-appliance/DEBIAN/prerm
	sudo svn co https://svn.erp5.org/repos/public/erp5/trunk/buildout $(SOFTWARE_BUILD_PATH)
	sudo chown -R `whoami` $(SOFTWARE_BUILD_PATH)
	sudo $(SOFTWARE_BUILD_PATH)/helpers/debian.lenny.sh
	cd $(SOFTWARE_BUILD_PATH); $(MAKE) $(MFLAGS)
	mkdir -p debian-erp5-appliance/$(PACKAGE_INSTALL_PATH)
	mv $(SOFTWARE_BUILD_PATH)/* debian-erp5-appliance/$(PACKAGE_INSTALL_PATH)
	rm -rf debian-erp5-appliance/*.txt
	rm -rf debian-erp5-appliance/*.TXT
	rm -rf `find debian-erp5-appliance/ -type d -name .svn`
	rm -rf `find debian-erp5-appliance/ -name *.pyc`
	dpkg-deb -b debian-erp5-appliance/ .

rpm-appliance:
	svn co https://svn.erp5.org/repos/public/erp5/trunk/utils/rpmgen rpmgen
	# set the correct name erp5-5.4.6
	sed -i "s,name = erp5-official-buildout,name = erp5-`cat VERSION.txt`,g" rpmgen/buildout.cfg
	# set the correct version defined in the main buildout
	sed -i "s,\$${checkout:location\}\/VERSION.txt,$(PACKAGE_VERSION),g" rpmgen/buildout.cfg
	# set the correct release
	if [ $(PACKAGE_RELEASE) != 'None' ]; then sed -i "s,release = mdv2010.0,release = $(PACKAGE_RELEASE),g" rpmgen/buildout.cfg; fi
	# it must use version defined in the main buildout
	sed -i "s,\$$(shell cat parts/checkout/VERSION.txt), `cat VERSION.txt`,g" rpmgen/Makefile
	sudo helpers/mandriva2010.0.sh
	# just make and wait...
	cd rpmgen; make
	# now we have the erp5 software rpm and we need it installed to build tiolive application rpm
	if test -d ~/rpmbuild/RPMS/x86_64; \
	then find ~/rpmbuild/RPMS/x86_64/ -name  erp5-`cat VERSION.txt`*.rpm -print0 | xargs -0 sudo urpmi --auto ; \
	else find ~/rpmbuild/RPMS/i586/ -name  erp5-`cat VERSION.txt`*.rpm -print0 | xargs -0 sudo urpmi --auto ; \
 	fi
	# building tiolive appliance
	sudo rpmbuild -bb rpmgen/spec/tiolive-application-buildout-mandriva2010.spec
