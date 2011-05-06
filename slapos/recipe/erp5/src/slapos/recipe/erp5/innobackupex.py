import os
import glob
def controller(args):
  """Creates full backup if not yet found, otherwise uses the newes full one
  to perform incremental"""
  innobackupex_incremental, innobackupex_full, full_backup, incremental_backup \
      = args
  if len(os.listdir(full_backup)) == 0:
    print 'Doing full backup in %r' % full_backup
    os.execv(innobackupex_full, [innobackupex_full, full_backup])
  backup_list = filter(os.path.isdir, glob.glob(full_backup + "/*"))
  backup_list.sort(key=lambda x: os.path.getmtime(x), reverse=True)
  base = backup_list[0]
  print 'Doing incremental backup in %r using %r as a base' % (
      incremental_backup, base)
  os.execv(innobackupex_incremental, [innobackupex_incremental,
    '--incremental-basedir=%s'%base, incremental_backup])
