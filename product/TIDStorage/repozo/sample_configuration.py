# COMMON
# This part is used both by tidstorage.py and repozo_tidstorage.py
known_tid_storage_identifier_dict = {
  "((('localhost', 8200),), '2')":
    ('/home/vincent/zeo2/var2/Data.fs',
     '/home/vincent/tmp/repozo/z22',
     'foo_test'),
  "((('localhost', 8200),), '1')":
    ('/home/vincent/zeo2/var/Data.fs',
     '/home/vincent/tmp/repozo/z21',
     'bar_test'),
  "((('localhost', 8100),), '1')":
    ('/home/vincent/zeo1/var/Data.fs',
     '/home/vincent/tmp/repozo/z11',
     'baz_test'),
}
base_url = 'http://login:password@localhost:5080/erp5/%s/modifyContext'
port = 9001
host = '127.0.0.1'

# SERVER
# This part is only used by server_v2.py
#logfile_name = 'tidstorage.log'
#pidfile_name = 'tidstorage.pid'
#fork = False
#setuid = None
#setgid = None
status_file = 'tidstorage.tid'
burst_period = 30
full_dump_period = 300

# REPOZO_TIDSTORAGE
# This part is only used by repozo_tidstorage.py
timestamp_file_path = 'repozo_tidstorage_timestamp.log'
# place to put backuped TIDStorage status_file logs
status_file_backup_dir = '/home/vincent/tmp/repozo'

