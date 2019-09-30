import os
import subprocess
import signal
import sys
import time
from asyncore import socket_map
from ZODB.DemoStorage import DemoStorage
from ZODB.FileStorage import FileStorage
from Products.ERP5Type.tests.utils import getMySQLArguments, instance_random

def _print(message):
  sys.stderr.write(message + "\n")

instance_home = os.environ['INSTANCE_HOME']
zserver_list = os.environ.get('zserver', '').split(',')
os.environ['zserver'] = zserver_list[0]

neo_storage = 'neo_storage' in os.environ
zeo_client = os.environ.get('zeo_client')
if zeo_client:
  zeo_client = zeo_client.rsplit(':', 1)
  zeo_client = (len(zeo_client) == 1 and 'localhost' or zeo_client[0],
                int(zeo_client[-1]))
try:
  activity_node = int(os.environ['activity_node'])
except KeyError:
  activity_node = (zeo_client or neo_storage or 'zeo_server' in os.environ
                  ) and 1 or None

data_fs_path = os.environ.get('erp5_tests_data_fs_path',
                              os.path.join(instance_home, 'var', 'Data.fs'))
load = int(os.environ.get('erp5_load_data_fs', 0))
save = int(os.environ.get('erp5_save_data_fs', 0))
save_mysql = int(os.environ.get('erp5_dump_sql') or not zeo_client) or None

dump_sql_path = os.path.join(instance_home, 'dump.sql')
if save_mysql:
  def save_mysql(verbosity=1):
    # The output of mysqldump needs to merge many lines at a time
    # for performance reasons (merging lines is at most 10 times
    # faster, so this produce somewhat not nice to read sql
    command = 'mysqldump %s > %s' % (getMySQLArguments(), dump_sql_path,)
    if verbosity:
      _print('Dumping MySQL database with %s ...' % command)
    subprocess.check_call(command, shell=True)

if load:
  if save_mysql:
    if os.path.exists(dump_sql_path):
      command = "mysql %s < %s" % (getMySQLArguments(), dump_sql_path)
      _print("Restoring MySQL database with %s ... " % command)
      _start = time.time()
      subprocess.check_call(command, shell=True)
      _print('done (%.3fs)\n' % (time.time() - _start))
    else:
      _print("Could not find MySQL dump (%r), will recreate catalog ... " % dump_sql_path)
      os.environ['erp5_tests_recreate_catalog'] = '1'
  _print("Restoring static files ... ")
else:
  if save and not (neo_storage or zeo_client) and os.path.exists(data_fs_path):
    _print("About to remove existing Data.fs %s (press Ctrl+C to abort)" % data_fs_path)
    time.sleep(5)
    os.remove(data_fs_path)

  # Whether passing --save or not passing both --load and --save, the catalog
  # must be cleared of data from previous execution if any
  _print("Catalog will be recreated to clear data (if any) from previous execution")
  import Products.ZMySQLDA.db
  sql_db = Products.ZMySQLDA.db.DB(os.environ['erp5_sql_connection_string'])
  table_list = sql_db.tables()
  if table_list:
    sql_db.query('DROP TABLE ' +
                 ','.join('`%s`' % table['TABLE_NAME'] for table in table_list))
  # Close SQL connection
  del sql_db

zeo_server_pid = None
node_pid_list = []

def fork():
  pid = os.fork()
  if pid:
    # make sure parent and child have 2 different RNG
    instance_random.seed(instance_random.random())
  return pid

def forkNodes():
  global node_pid_list
  for i in xrange(1, activity_node):
    pid = fork()
    if not pid:
      node_pid_list = None
      os.environ['zserver'] = i < len(zserver_list) and zserver_list[i] or ''
      break
    node_pid_list.append(pid)

cluster = True

if neo_storage:
  if zeo_client:
    sys.exit("--neo_storage conflicts with --zeo_client")
  demo_storage = load and not save
  if activity_node > 1 and demo_storage:
    sys.exit("--save is required when running several"
             " zope nodes on an existing NEO database")
  from neo.lib import logging
  from neo.tests.functional import NEOCluster
  logging.backlog()
  storage_count = 2
  if load or save:
      db_list = [os.path.join(instance_home, 'var', 'neo%u.sqlite' % i)
                 for i in xrange(1, storage_count+1)]
  else:
      db_list = [None] * storage_count
  cwd = os.getcwd()
  neo_cluster = NEOCluster(db_list, partitions=4, name='erp5/unit_test',
                           temp_dir=cwd, logger=save,
                           adapter='SQLite', clear_databases=not load)
  forkNodes()
  if node_pid_list is None:
      save_mysql = None
  else:
      cluster = bool(node_pid_list)
      sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)
      try:
          neo_cluster.start()
      finally:
          signal.signal(signal.SIGINT, sigint)
  Storage = neo_cluster.getZODBStorage(read_only=demo_storage)
  if demo_storage:
      Storage = DemoStorage(base=Storage)
else:
  neo_cluster = None
  while not zeo_client:
    if activity_node:
      r, zeo_client = os.pipe()
      zeo_server_pid = fork()
      if zeo_server_pid:
        save_mysql = None
        os.close(zeo_client)
        zeo_client = eval(os.fdopen(r).read())
        continue
      else:
        node_pid_list = activity_node = None
        os.close(r)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    elif activity_node is not None:
      # run ZEO server but no need to fork
      zeo_server_pid = 0
    else:
      cluster = False

    if save:
      Storage = FileStorage(data_fs_path)
    elif load:
      Storage = FileStorage(data_fs_path, read_only=True)
      Storage = DemoStorage(base=Storage)
    else:
      Storage = DemoStorage()
    break
  else:
    forkNodes()
    from ZEO.ClientStorage import ClientStorage
    Storage = ClientStorage(zeo_client)

if node_pid_list is not None:
  _print("Instance at %r loaded ... " % instance_home)
