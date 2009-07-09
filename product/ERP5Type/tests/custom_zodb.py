import os
import shutil
import glob
import ZODB
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage
from Products.ERP5Type.tests.utils import getMySQLArguments

instance_home = os.environ.get('INSTANCE_HOME')
data_fs_path = os.environ.get('erp5_tests_data_fs_path',
                              os.path.join(instance_home, 'Data.fs'))
load = int(os.environ.get('erp5_load_data_fs', 0))
save = int(os.environ.get('erp5_save_data_fs', 0))

if load:
  dump_sql = os.path.join(instance_home, 'dump.sql')
  if os.path.exists(dump_sql):
    print("Restoring MySQL database ... ")
    ret = os.system("mysql %s < %s" % (getMySQLArguments(), dump_sql))
    assert not ret
  else:
    os.environ['erp5_tests_recreate_catalog'] = '1'
  print("Restoring static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet', 'Extensions'):
    if os.path.exists(os.path.join(instance_home, '%s.bak' % dir)):
      full_path = os.path.join(instance_home, dir)
      shutil.rmtree(full_path)
      shutil.copytree(os.path.join(instance_home, '%s.bak' % dir),
                      full_path, symlinks=True)
else:
  print("Cleaning static files ... ")
  for dir in ('Constraint', 'Document', 'PropertySheet', 'Extensions'):
    full_path = os.path.join(instance_home, dir)
    if os.path.exists(full_path):
      assert os.path.isdir(full_path)
      for f in glob.glob('%s/*' % full_path):
        os.unlink(f)
  if save and os.path.exists(data_fs_path):
    os.remove(data_fs_path)

if save:
  Storage = FileStorage(data_fs_path)
elif load:
  Storage = DemoStorage(base=FileStorage(data_fs_path), quota=(1<<20))
else:
  Storage = DemoStorage(quota=(1<<20))
