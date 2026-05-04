from App.config import getConfiguration
import os

try:
    erp5_catalog_storage = getConfiguration().product_config['initsite'].get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog')
except KeyError:
    # in test
    erp5_catalog_storage = os.environ.get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog')

from Products.Database import db, DA
db.configure(erp5_catalog_storage)
DA.configure(erp5_catalog_storage)