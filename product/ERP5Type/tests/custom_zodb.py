import ZODB
import os
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage
from Products.ERP5Type.tests.utils import getMySQLArguments

instance_home = os.environ.get('INSTANCE_HOME')
data_fs_path = os.environ.get('erp5_tests_data_fs_path')
new_data_fs_path = os.path.join(instance_home, 'Data.fs')

if os.environ.get('erp5_load_data_fs'):
  if os.environ.get('erp5_force_data_fs'):
    Storage = FileStorage(new_data_fs_path)
  else:
    Storage = DemoStorage(base=FileStorage(new_data_fs_path), quota=(1<<20))
  print("Restoring MySQL database ... ")
  assert os.system("mysql %s < %s/dump.sql" % (
                getMySQLArguments(), instance_home)) == 0
  print("Restoring static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet', 'Extensions'):
    if os.path.exists('%s/%s.bak' % (instance_home, dir)):
      assert os.system('rm -rf %s/%s' % (instance_home, dir)) == 0
      assert os.system('cp -ar %s/%s.bak %s/%s' % (
                instance_home, dir, instance_home, dir)) == 0
elif os.environ.get('erp5_save_data_fs'):
  print("Cleaning static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet', 'Extensions'):
    if os.path.exists('%s/%s' % (instance_home, dir)):
      assert os.system('rm -f %s/%s/*' % (instance_home, dir)) == 0
  if os.path.exists(new_data_fs_path):
    os.remove(new_data_fs_path)
  Storage = FileStorage(new_data_fs_path)
elif data_fs_path:
  Storage = DemoStorage(base=FileStorage(data_fs_path), quota=(1<<20))
else:
  Storage = DemoStorage(quota=(1<<20))
