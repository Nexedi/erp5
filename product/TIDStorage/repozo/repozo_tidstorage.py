#!/usr/bin/python2.4

##############################################################################
#
# Copyright (c) 2007 Nexedi SARL. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
# Parts of this file are borrowed from Zope 2.8.8 repozo.py script.
# Essentialy "usage" and "parseargs" methods.
# So it's released under the ZPL v2.0, as is Zope 2.8.8 .

""" repozo wrapper to backup for multiple Data.fs files and restore them in a consistent way.

Usage: %(program)s [-h|--help] [-c|--config configuration_file]
       [--repozo repozo_command] [-R|--recover|--recover_check]
       [--tid_log tid_log_file]
       [...]

  -h
  --help
    Display this help and exit.

  -c configuration_file
  --config configuration_file
    Use given file as configuration file.
    It must be a python file. See sample_configuration.py for required values.
    Recquired if neither -h nor --help are given.

  --repozo repozo_command
    Use given executable as repozo command.
    Default: repozo.py

  -R
  --recover
    Instead of saving existing Data.fs, perform an automated recovery from
    backups + timestamp file with optionally cutting file at found transaction.

  --recover_check
    Similar to above, except that it restores file to temp folder and compares
    with existing file.
    Files restored this way are automaticaly deleted after check.
  
  -t tid_log_file
  --tid_log tid_log_file
    TID log file, which will be used to find TID, which then will be used to
    cut restored file at found TID
"""

import imp
import getopt
import sys
import os
import md5
import time
import tempfile
from shutil import copy

from repozo.restore_tidstorage import parse, get_tid_position

program = sys.argv[0]

def log(message):
  print message

def backup(known_tid_storage_identifier_dict, repozo_formated_command):
  """Backups all ZODB files"""
  backup_count = 0
  total_count = len(known_tid_storage_identifier_dict)
  for key, (file_path, storage_path, object_path) in known_tid_storage_identifier_dict.iteritems():
    repozo_command = repozo_formated_command % (storage_path, file_path)
    if not os.access(storage_path, os.R_OK):
      os.makedirs(storage_path)
    log('Runing %r...' % (repozo_command, ))
    status = os.system(repozo_command)
    status = os.WEXITSTATUS(status)
    if status == 0:
      backup_count += 1
    else:
      log('Error occurred while saving %s: exit status=%i' % (file_path, status))
  log('Saved %i FileStorages out of %i.' % (backup_count, total_count))
  return total_count - backup_count

def get_md5_diggest(file_instance, length):
  BLOCK_SIZE=512
  file_instance.seek(0)
  md5sum = md5.new()
  read = file_instance.read
  update = md5sum.update
  while length > 0:
    to_read = min(BLOCK_SIZE, length)
    buffer = read(to_read)
    if len(buffer) != to_read:
      log('Warning: read %i instead of requested %i, stopping read' % (len(buffer), to_read))
      length = 0
    else:
      length -= to_read
    update(buffer)
  return md5sum.hexdigest()

def recover(known_tid_storage_identifier_dict, repozo_formated_command, check=False, last_tid_dict=None):
  """Recovers all ZODB files, when last_tid_dict is passed cut them at proper byte"""
  recovered_count = 0
  total_count = len(known_tid_storage_identifier_dict)
  result = 0
  for key, (file_path, storage_path, object_path) in known_tid_storage_identifier_dict.iteritems():
    # check that indexes do not exists if cut shall be done
    file_index = file_path + ".index"
    if os.access(file_index, os.F_OK) and last_tid_dict is not None:
      log('Error: Index file %s exists. Bug in ZODB makes it impossible to cut'
          ' indexed file after restore. Cannot continue.' %
        file_index)
      result = 1
  if result:
    return result
  for key, (file_path, storage_path, object_path) in known_tid_storage_identifier_dict.iteritems():
    if not os.access(storage_path, os.R_OK):
      log('Warning: unable to recover %s because %s is missing/unreadable.' % (file_path, storage_path))
      continue
    if check:
      original_file_path = file_path
      file_path = os.path.join(tempfile.gettempdir(), os.path.basename(file_path))
    repozo_command = repozo_formated_command % (storage_path, file_path)
    status = os.system(repozo_command)
    status = os.WEXITSTATUS(status)
    if status == 0:
      recovered_count += 1
      if last_tid_dict is not None:
        pos = get_tid_position(file_path, last_tid_dict[key])
        print 'Cutting restored file %s at %s byte' % (file_path, pos),
        f = open(file_path,'a')
        if not check:
          f.truncate(pos)
          print
        else:
          print 'only check, file untouched'
        f.close()
    else:
      log('Error occurred while recovering %s: exit status=%i' % (file_path, status))
    if check:
      log('Info: Comparing restored %s with original %s' % (file_path, original_file_path))
      recovered_file = open(file_path, 'r')
      original_file = open(original_file_path, 'r')
      try:
        recovered_file.seek(0, 2)
        original_file.seek(0, 2)
        recovered_file_length = recovered_file.tell()
        original_file_length = original_file.tell()
        checked_length = recovered_file_length
        if recovered_file_length < original_file_length:
          log('Info: Shorter than original: -%i bytes (-%.02f%%)' % \
              (original_file_length - recovered_file_length,
               1 - (float(recovered_file_length) / original_file_length)))
        elif recovered_file_length > original_file_length:
          log('ERROR: Longer than original: +%i bytes (+%.02f%%). Was original packed since backup ?' % \
              (recovered_file_length - original_file_length,
               float(recovered_file_length) / original_file_length))
          checked_length = None
        if checked_length is not None:
          recovered_file_diggest = get_md5_diggest(recovered_file, checked_length)
          original_file_diggest = get_md5_diggest(original_file, checked_length)
          if recovered_file_diggest != original_file_diggest:
            log('ERROR: Recovered md5 does not match original: %s != %s.' % \
                (recovered_file_diggest, original_file_diggest))
      finally:
        recovered_file.close()
        original_file.close()
      os.unlink(file_path)

  log('Restored %i FileStorages out of %i.' % (recovered_count, total_count))
  return total_count - recovered_count

def usage(code, msg=''):
  outfp = sys.stderr
  if code == 0:
    outfp = sys.stdout

  print >> outfp, __doc__ % globals()
  if msg:
    print >> outfp, msg

  sys.exit(code)

def parseargs():
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'vQrt:FhzRc:',
                               ['help', 'verbose', 'quick', 'full',
                                'gzip', 'repository', 'repozo=',
                                'config=','recover', 'recover_check',
                                'tid_log='])
  except getopt.error, msg:
    usage(1, msg)

  class Options:
    timestamp_file_path = None
    repozo_file_name = 'repozo.py'
    configuration_file_name = None
    repozo_opts = ['-B']
    known_tid_storage_identifier_dict = {}
    recover = False
    dry_run = False
    status_file = None
    status_file_backup_dir = None
    recover_status_file = None

  options = Options()

  if args:
    options.repozo_opts.extend(args)

  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage(0)
    elif opt in ('-c', '--config'):
      options.configuration_file_name = arg
    elif opt == '--repozo':
      options.repozo_file_name = arg
    elif opt in ('-R', '--recover', '--recover_check'):
      options.repozo_opts[0] = '-R'
      options.recover = True
      if opt == '--recover_check':
        options.dry_run = True
    elif opt in ('-r', '--repository'):
      options.repozo_opts.append('%s %s' % (opt, arg))
    elif opt in ('-t', '--tid_log'):
      options.recover_status_file = arg
    else:
      options.repozo_opts.append(opt)

  if options.configuration_file_name is None:
    usage(1, 'Either -c or --config is required.')

  configuration_filename, ext = os.path.splitext(os.path.basename(options.configuration_file_name))
  configuration_path = os.path.dirname(options.configuration_file_name)
  if len(configuration_path):
    configuration_path = [configuration_path]
  else:
    configuration_path = sys.path
  file, path, description = imp.find_module(configuration_filename, configuration_path)
  module = imp.load_module(configuration_filename, file, path, description)
  file.close()
  try:
    options.known_tid_storage_identifier_dict = module.known_tid_storage_identifier_dict
    options.timestamp_file_path = module.timestamp_file_path
  except AttributeError, msg:
    usage(1, msg)
  for option_id in ('status_file', 'status_file_backup_dir' ):
    if getattr(options, option_id) is None:
      setattr(options, option_id, getattr(module, option_id, None))
  # XXX: we do not check any option this way, it's too dangerous.
  #options.repozo_opts.extend(getattr(module, 'repozo_opts', []))

  return options

def backupStatusFile(status_file,destination_directory):
  file_name = os.path.basename(status_file) + '-' + '%04d-%02d-%02d-%02d-%02d-%02d' % time.gmtime()[:6]
  copy(status_file, os.path.sep.join((destination_directory,file_name)))
  log("Written status file backup as %s" % os.path.sep.join((destination_directory,file_name)))
  
def main():
  options = parseargs()
  if not options.recover and options.recover_status_file:
    raise ValueError("Status file path only for recovering")

  last_tid_dict = None
  if options.recover_status_file:
    last_tid_dict = parse(options.recover_status_file)

  repozo_formated_command = '%s %s -r "%%s"' % (options.repozo_file_name, ' '.join(options.repozo_opts))
  if options.recover:
    timestamp_file = open(options.timestamp_file_path, 'r')
    timestamp = ''
    read_line = ' '
    while len(read_line):
      timestamp = read_line
      read_line = timestamp_file.readline()
    timestamp = timestamp.strip('\r\n \t')
    if timestamp is not None:
      repozo_formated_command += ' -o "%%s" -D %s' % (timestamp, )
    result = recover(
      known_tid_storage_identifier_dict=options.known_tid_storage_identifier_dict,
      repozo_formated_command=repozo_formated_command,
      check=options.dry_run,
      last_tid_dict=last_tid_dict)
  else:
    repozo_formated_command += ' -f "%s"'
    if options.status_file is not None and options.status_file_backup_dir is not None:
      backupStatusFile(options.status_file, options.status_file_backup_dir)
    result = backup(
      known_tid_storage_identifier_dict=options.known_tid_storage_identifier_dict,
      repozo_formated_command=repozo_formated_command)
    if result == 0:
      # Paranoid mode:
      # Issue a system-wide "sync" command to make sure all files which were saved
      # are really present on disk.
      os.system('sync')
      timestamp_file = open(options.timestamp_file_path, 'a', 0)
      try:
        # Borrowed from repozo.
        timestamp_file.write('\n%04d-%02d-%02d-%02d-%02d-%02d' % time.gmtime()[:6])
      finally:
        timestamp_file.close()
  return result

if __name__ == '__main__':
  sys.exit(main())
