import ZODB
import os
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage
from Products.ERP5Type.tests.utils import getMySQLArguments

instance_home = os.environ.get('INSTANCE_HOME')
data_fs_path = os.environ.get('erp5_tests_data_fs_path')
new_data_fs_path = os.path.join(instance_home, 'Data.fs')

if os.environ.get('erp5_save_data_fs'):
  if os.path.exists(new_data_fs_path):
    os.remove(new_data_fs_path)
  Storage = FileStorage(new_data_fs_path)
elif os.environ.get('erp5_load_data_fs'):
  if os.environ.get('erp5_force_data_fs'):
    Storage = FileStorage(new_data_fs_path)
  else:
    Storage = DemoStorage(base=FileStorage(new_data_fs_path), quota=(1<<20))
  print("Restoring MySQL database ... ")
  os.system("mysql %s < %s/dump.sql" % (getMySQLArguments(), instance_home))
  print("Restoring static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet'):
    if os.path.exists('%s/%s.bak' % (instance_home, dir)):
      os.system('rm -rf %s/%s' % (instance_home, dir))
      os.system('cp -ar %s/%s.bak %s/%s' % (instance_home, dir, instance_home, dir))
elif data_fs_path:
  Storage = DemoStorage(base=FileStorage(data_fs_path), quota=(1<<20))
else:
  Storage = DemoStorage(quota=(1<<20))
