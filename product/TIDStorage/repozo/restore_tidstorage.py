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
# Essentialy "usage", "parseargs" and parts of "restore" methods.
# So it's released under the ZPL v2.0, as is Zope 2.8.8 .

"""
Usage: %(program)s [-h|--help] [-c|--config configuration_file]

  -h
  --help
    Display this help and exit.

  -c configuration_file
  --config configuration_file
    Use given file as configuration file.
    It must be a python file.
    Recquired if neither -h nor --help are given.
"""

import imp
import getopt
import sys
import os
# urllib2 does not support (?) urls containing credentials
# (http://login:password@...) but it's fine with urllib.
from struct import pack
import shutil
from ZODB.FileStorage import FileStorage

program = sys.argv[0]

def log(message):
  print message

def parse(status_file):
  tid_log = open(status_file)
  content = {}
  last_timestamp = None

  line = tid_log.readline()
  while line != '':
    split_line = line.split(' ', 2)
    assert len(split_line) == 3, repr(split_line)
    line_timestamp, line_type, line_dict = split_line
    line_timestamp = float(line_timestamp)
    assert line_type in ('f', 'd'), repr(line_type)
    if last_timestamp is None:
      last_timestamp = line_timestamp
    else:
      assert last_timestamp < line_timestamp, '%r < %r' % (last_timestamp, line_timestamp)
    line_dict = eval(line_dict, None)
    assert isinstance(line_dict, dict), type(line_dict)
    assert len(line_dict), repr(line_dict)
    if line_type == 'd':
      for key, value in line_dict.iteritems():
        if key in content:
          assert content[key] < value, '%r < %r' % (content[key], value)
        content[key] = value
    elif line_type == 'f':
      for key, value in content.iteritems():
        assert key in line_dict, repr(key)
        assert value <= line_dict[key], '%r <= %r' % (value, line_dict[key])
      content = line_dict
    line = tid_log.readline()
  return content

READCHUNK = 10 * 1024 * 1024

def recover(data_fs_backup_path_dict, status_file):
  last_tid_dict = parse(status_file)
  for storage_id, (file_path, backup_path) in data_fs_backup_path_dict.iteritems():
    # Derived from repozo (function=do_full_backup)
    # TODO: optimise to read backup only once.
    can_restore = False
    if os.path.exists(backup_path):
      if os.path.exists(file_path):
        print 'Both original and backup files exist for %r. If previous restoration was successful, you should delete the backup for this restoration to take place. Original: %r Backup: %r' % (storage_id, file_path, backup_path)
      else:
        print 'Only backup file is available for %r: %r. Assuming it\'s ok and restoring to %r' % (storage_id, backup_path, file_path)
        can_restore = True
    else:
      if os.path.exists(file_path):
        sys.stdout.write('Copying %r to %r... ' % (file_path, backup_path))
        shutil.copy(file_path, backup_path)
        initial_size = stat(file_path).st_size
        final_size = stat(backup_path).st_size
        if initial_size == final_size:
          can_restore = True
          print 'Done.'
        else:
          print 'Backup size %i differs from original size %i. Is the original file (%r) still in use ? Is there enough free disk space at destination (%r) ?' % (final_size, initial_size, file_path, backup_path)
      else:
        print 'Cannot find any file for %r: %r and %r do not exist.' % (storage_id, file_path, backup_path)
    if can_restore:
      last_tid = last_tid_dict[storage_id] + 1
      tid = pack('>Q', last_tid)
      # Find the file position of the last completed transaction.
      fs = FileStorage(backup_path, read_only=True, stop=tid)
      # Note that the FileStorage ctor calls read_index() which scans the file
      # and returns "the position just after the last valid transaction record".
      # getSize() then returns this position, which is exactly what we want,
      # because we only want to copy stuff from the beginning of the file to the
      # last valid transaction record.
      pos = fs.getSize()
      fs.close()
      print 'Restoring backup: %s bytes (transaction %r) from %s to %s' % (pos, tid, backup_path, file_path)
      source_file = open(backup_path, 'rb')
      destination_file = open(file_path, 'wb')
      while pos:
        todo = min(READCHUNK, pos)
        data = source_file.read(todo)
        if not data:
          print 'Unexpected end of data stream (should contain %i more bytes)' % (pos, )
          break
        destination_file.write(data)
        pos -= len(data)
      destination_file.close()
      source_file.close()
    else:
      print 'Skipping restoration of %r (%r).' % (file_path, storage_id)

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
    opts, args = getopt.getopt(sys.argv[1:], 'hc:',
                               ['help', 'config='])
  except getopt.error, msg:
    usage(1, msg)

  class Options:
    configuration_file_name = None
    status_file = None

  options = Options()

  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage(0)
    elif opt in ('-c', '--config'):
      options.configuration_file_name = arg

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
    options.data_fs_backup_path_dict = module.data_fs_backup_path_dict
    options.status_file = module.status_file
  except AttributeError, msg:
    usage(1, msg)
  return options

def main():
  options = parseargs()
  recover(
    data_fs_backup_path_dict=options.data_fs_backup_path_dict,
    status_file=options.status_file)

if __name__ == '__main__':
  sys.exit(main())
