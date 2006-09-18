import ZODB
import os
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage

data_fs_path = os.environ.get('erp5_tests_data_fs_path')
if data_fs_path:
  Storage = DemoStorage(base=FileStorage(data_fs_path), quota=(1<<20))
else:
  Storage = DemoStorage(quota=(1<<20))

