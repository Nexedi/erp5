import os
import shutil
import glob
import ZODB
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
  ret = os.system("mysql %s < %s/dump.sql" % (
                getMySQLArguments(), instance_home))
  assert ret == 0
  print("Restoring static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet', 'Extensions'):
    if os.path.exists(os.path.join(instance_home, '%s.bak' % dir)):
      full_path = os.path.join(instance_home, dir)
      shutil.rmtree(full_path)
      shutil.copytree(os.path.join(instance_home, '%s.bak' % dir),
                      full_path, symlinks=True)
elif os.environ.get('erp5_save_data_fs'):
  print("Cleaning static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet', 'Extensions'):
    full_path = os.path.join(instance_home, dir)
    if os.path.exists(full_path):
      assert os.path.isdir(full_path)
      for f in glob.glob('%s/*' % full_path):
        os.unlink(f)
  if os.path.exists(new_data_fs_path):
    os.remove(new_data_fs_path)
  Storage = FileStorage(new_data_fs_path)
elif data_fs_path:
  Storage = DemoStorage(base=FileStorage(data_fs_path), quota=(1<<20))
else:
  Storage = DemoStorage(quota=(1<<20))
