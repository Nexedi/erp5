# 
# Makefile in order to create rpm files for ERP5
# and all is components
#

RPM_PATH=/home/$(USER)/rpm

all: base18-spec zsqlcatalog-spec erp5-spec coramy-spec erp5compatibility-spec \
	erp5type-spec erp5syncml-spec erp5catalog-spec erp5form-spec cmfcategory-spec \
	construct-all

clean:
	rm -rf /home/$(USER)/rpm/RPMS/i586/*
	rm -rf /home/$(USER)/rpm/SRPMS/*

# For nexedi, same as above and the synchronyzation
# with the rpm server
nex-all: all list sync

nex-update: list sync

# For each rpm, we call build-spec
cmfcategory-spec: 
	build-spec CMFCategory
erp5compatibility-spec: 
	build-spec ERP5Compatibility
erp5type-spec: 
	build-spec ERP5Type
erp5syncml-spec: 
	build-spec ERP5SyncML
erp5catalog-spec: 
	build-spec ERP5Catalog
erp5-spec: 
	build-spec ERP5
erp5form-spec: 
	build-spec ERP5Form
base18-spec: 
	build-spec Base18
zsqlcatalog-spec: 
	build-spec ZSQLCatalog
coramy-spec: 
	build-spec Coramy
construct-all:
	rpmbuild --sign -ba CMFCategory.spec ERP5Compatibility.spec ERP5Type.spec ERP5SyncML.spec ERP5Catalog.spec ERP5.spec ERP5Form.spec Base18.spec ZSQLCatalog.spec Coramy.spec

# create the synthesis.hdlist.cz file
list: 
	-rsync -av $(RPM_PATH)/RPMS/i586/*.rpm $(RPM_PATH)/nexRPMS/
	-rsync -av $(RPM_PATH)/SRPMS/*.rpm $(RPM_PATH)/nexSRPMS/
	genhdlist $(RPM_PATH)/nexSRPMS/
	genhdlist $(RPM_PATH)/nexRPMS/

# Synchronization with the nexedi server
sync:
	-rsync -rlvpugtz -e ssh --progress --stats $(RPM_PATH)/nexRPMS/ $(USER)@nexedi.org:/var/www/html/nexedi.org/static/RPMS/
	-rsync -rlvpugtz -e ssh --progress --stats $(RPM_PATH)/nexRPMS/ $(USER)@nexedi.org:/var/www/html/nexedi.org/static/RPMS/

