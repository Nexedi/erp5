#
# Makefile in order to create rpm files for ERP5
# and all is components
#

RPM_PATH=/home/$(USER)/rpm

all: zsqlcatalog-spec erp5-spec \
	erp5type-spec erp5syncml-spec erp5catalog-spec erp5form-spec cmfcategory-spec \
	cmfactivity-spec construct-all list

clean:
	rm -rf /home/$(USER)/rpm/RPMS/i586/*
	rm -rf /home/$(USER)/rpm/RPMS/noarch/*
	rm -rf /home/$(USER)/rpm/SRPMS/*

# For nexedi, same as above and the synchronyzation
# with the rpm server
nex-all: nex-all-10.0
nex-all-9.1: all list-9.1 sync-9.1
nex-all-9.2: all list-9.2 sync-9.2
nex-all-10.0: all list-10.0 sync-10.0

nex-update: list sync

# For each rpm, we call build-spec
cmfcategory-spec: 
	build-spec CMFCategory
cmfactivity-spec: 
	build-spec CMFActivity
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
copy: 
	#-rsync -rva $(RPM_PATH)/* /mnt/mdk/rpm/
	-rsync -rva $(RPM_PATH)/nexRPMS-mdk-10.0/* /mnt/mdk_cooker/rpm/nexRPMS-mdk-10.0/
	-rsync -rva $(RPM_PATH)/nexRPMS-mdk-10.0/* /mnt/mdk-10.0/rpm/nexRPMS-mdk-10.0/
construct-all:
	rpmbuild -ba CMFCategory.spec ERP5Type.spec ERP5SyncML.spec ERP5Catalog.spec ERP5.spec ERP5Form.spec ZSQLCatalog.spec CMFActivity.spec

# create the synthesis.hdlist.cz file
list: list-10.0 copy

list-9.1: 
	-rsync -av $(RPM_PATH)/RPMS/i586/*.rpm $(RPM_PATH)/nexRPMS-mdk-9.1/
	-rsync -av $(RPM_PATH)/RPMS/noarch/*.rpm $(RPM_PATH)/nexRPMS-mdk-9.1/
	-rsync -av $(RPM_PATH)/SRPMS/*.rpm $(RPM_PATH)/nexSRPMS-mdk-9.1/
	genhdlist $(RPM_PATH)/nexSRPMS-mdk-9.1/
	genhdlist $(RPM_PATH)/nexRPMS-mdk-9.1/

list-9.2: 
	-rsync -av $(RPM_PATH)/RPMS/i586/*.rpm $(RPM_PATH)/nexRPMS-mdk-9.2/
	-rsync -av $(RPM_PATH)/RPMS/noarch/*.rpm $(RPM_PATH)/nexRPMS-mdk-9.2/
	-rsync -av $(RPM_PATH)/SRPMS/*.rpm $(RPM_PATH)/nexSRPMS-mdk-9.2/
	genhdlist $(RPM_PATH)/nexSRPMS-mdk-9.2/
	genhdlist $(RPM_PATH)/nexRPMS-mdk-9.2/

list-10.0: 
	-mkdir $(RPM_PATH)/nexRPMS-mdk-10.0/
	-mkdir $(RPM_PATH)/nexSRPMS-mdk-10.0/
	-rsync -av $(RPM_PATH)/RPMS/i586/*.rpm $(RPM_PATH)/nexRPMS-mdk-10.0/
	-rsync -av $(RPM_PATH)/RPMS/noarch/*.rpm $(RPM_PATH)/nexRPMS-mdk-10.0/
	-rsync -av $(RPM_PATH)/SRPMS/*.rpm $(RPM_PATH)/nexSRPMS-mdk-10.0/
	-cd $(RPM_PATH)/nexSRPMS-mdk-10.0/ && genhdlist .
	-cd $(RPM_PATH)/nexRPMS-mdk-10.0/ && genhdlist .

# Synchronization with the nexedi server
sync: sync-10.0

sync-9.1:
	-rsync -rlvputz -e ssh --progress --partial --stats $(RPM_PATH)/nexRPMS-mdk-9.1/ $(USER)@smets.com:/var/www/html/nexedi.org/static/Mandrake/9.1/RPMS/
	-rsync -rlvputz -e ssh --progress --partial --stats $(RPM_PATH)/nexSRPMS-mdk-9.1/ $(USER)@smets.com:/var/www/html/nexedi.org/static/Mandrake/9.1/SRPMS/

sync-9.2:
	-rsync -rlvputz -e ssh --progress --partial --stats $(RPM_PATH)/nexRPMS-mdk-9.2/ $(USER)@smets.com:/var/www/html/nexedi.org/static/Mandrake/9.2/RPMS/
	-rsync -rlvputz -e ssh --progress --partial --stats $(RPM_PATH)/nexSRPMS-mdk-9.2/ $(USER)@smets.com:/var/www/html/nexedi.org/static/Mandrake/9.2/SRPMS

sync-10.0:
	-rsync -rlvputz -e ssh --progress --partial --stats $(RPM_PATH)/nexRPMS-mdk-10.0/ $(USER)@smets.com:/var/www/html/nexedi.org/static/Mandrake/10.0/RPMS/
	-rsync -rlvputz -e ssh --progress --partial --stats $(RPM_PATH)/nexSRPMS-mdk-10.0/ $(USER)@smets.com:/var/www/html/nexedi.org/static/Mandrake/10.0/SRPMS

