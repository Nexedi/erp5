from App.config import getConfiguration
import os

try:
    erp5_catalog_storage = getConfiguration().product_config['initsite'].get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog')
except KeyError:
    # in test
    erp5_catalog_storage = os.environ.get('erp5_catalog_storage', 'erp5_mysql_innodb_catalog')

from . import SQLBase
SQLBase.configure(erp5_catalog_storage)
from . import SQLDict, SQLJoblib
SQLDict.configure(erp5_catalog_storage)
SQLJoblib.configure(erp5_catalog_storage)
from . import SQLQueue
from Products.CMFActivity import ActivityTool
ActivityTool.activity_dict.update(
    {k: getattr(v, k)()
    for k, v in {'SQLDict': SQLDict, 'SQLQueue': SQLQueue, 'SQLJoblib': SQLJoblib}.items()})