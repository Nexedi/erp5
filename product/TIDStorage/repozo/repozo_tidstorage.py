#!/usr/bin/python

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

""" repozo wrapper to backup for multiple Data.fs files in a consistent way.

Usage: %(program)s [-h|--help] [-c|--config configuration_file]
       [--repozo repozo_command] [-R|--recover|--recover_check]
       [-H|--host address] [-p|--port port_number] [-u|--url formated_url]
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
    backups + timestamp file.

  --recover_check
    Similar to above, except that it restores file to temp folder and compares
    with existing file.
    Files restored this way are automaticaly deleted after check.
  
  -H address
  --host address
    TIDStorage server host address.
    Overrides setting found in configuration_file.
    Not required if recovering (see above).

  -p port_number
  --port port_number
    TIDStorage port nuber.
    Overrides setting found in configuration_file.
    Not required if recovering (see above).

  -u formated_url
  --url formated_url
    Zope base url, optionnaly with credentials.
    Overrides setting found in configuration_file.
    Not required if recovering (see above).

  All others parameters are transmitted to repozo but are partly processed by
  getopt. To transmit unprocessed parameters to repozo, pass them as an
  argument.
"""

from tests.testTIDServer import TIDClient
from ExchangeProtocol import ExchangeProtocol

import socket
import base64
import imp
import getopt
import sys
import os
# urllib2 does not support (?) urls containing credentials
# (http://login:password@...) but it's fine with urllib.
from urllib import urlopen
import traceback
import md5
import time
import tempfile
from struct import pack

program = sys.argv[0]

def log(message):
  print message

def backup(address, known_tid_storage_identifier_dict, repozo_formated_command, zope_formated_url=None):
  connection = TIDClient(address)
  to_load = known_tid_storage_identifier_dict.keys()
  load_count = 2
  while len(to_load):
    if load_count < 1:
      raise ValueError('It was impossible to retrieve all required TIDs. Missing: %s' % to_load)
    to_load = []
    load_count -= 1
    stored_tid_dict = connection.dump_all()
    #log(stored_tid_dict)
    for key, (file_path, storage_path, object_path) in known_tid_storage_identifier_dict.iteritems():
      if key not in stored_tid_dict and zope_formated_url is not None:
        to_load.append(key)
        if object_path is not None:
          serialize_url = zope_formated_url % (object_path, )
          log(serialize_url)
          try:
            response = urlopen(serialize_url)
          except Exception, message:
            # Prevent exceptions from interrupting the backup.
            # We don't care about how well the web server is working, the only
            # important thing is to get all TIDs in TIDStorage, and it's checked
            # later.
            log(''.join(traceback.format_exception(*sys.exc_info())))

  backup_count = 0
  total_count = len(known_tid_storage_identifier_dict)
  for key, (file_path, storage_path, object_path) in known_tid_storage_identifier_dict.iteritems():
    tid_as_int = stored_tid_dict[key] + 1
    tid = base64.encodestring(pack('>Q', tid_as_int)).rstrip()
    repozo_command = repozo_formated_command % (storage_path, file_path, tid)
    if not os.access(storage_path, os.R_OK):
      os.makedirs(storage_path)
    log('Runing %r...' % (repozo_command, ))
    status = os.system(repozo_command)
    status = os.WEXITSTATUS(status)
    if status == 0:
      backup_count += 1
    else:
      log('Error occured while saving %s: exit status=%i' % (file_path, status))
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
      log('Warning: read %i instead of requiested %i, stopping read' % (len(buffer), to_read))
      length = 0
    else:
      length -= to_read
    update(buffer)
  return md5sum.hexdigest()

def recover(known_tid_storage_identifier_dict, repozo_formated_command, check=False):
  recovered_count = 0
  total_count = len(known_tid_storage_identifier_dict)
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
    else:
      log('Error occured while recovering %s: exit status=%i' % (file_path, status))
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
    opts, args = getopt.getopt(sys.argv[1:], 'vQr:FhzMRc:H:p:u:',
                               ['help', 'verbose', 'quick', 'full',
                                'gzip', 'print-max-tid', 'repository',
                                'repozo=', 'config=', 'host=', 'port=',
                                'url=', 'recover', 'recover_check'])
  except getopt.error, msg:
    usage(1, msg)

  class Options:
    timestamp_file_path = None
    repozo_file_name = 'repozo.py'
    configuration_file_name = None
    repozo_opts = ['-B']
    host = None
    port = None
    base_url = None
    known_tid_storage_identifier_dict = {}
    recover = False
    dry_run = False

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
    elif opt in ('-H', '--host'):
      options.host = arg
    elif opt in ('-p', '--port'):
      try:
        options.port = int(port)
      except ValueError, msg:
        usage(1, msg)
    elif opt in ('-u', '--url'):
      options.url = arg
    elif opt in ('-r', '--repository'):
      options.repozo_opts.append('%s %s' % (opt, arg))
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
  for option_id in ('port', 'host', 'base_url'):
    if getattr(options, option_id) is None:
      setattr(options, option_id, getattr(module, option_id, None))
  # XXX: we do not check any option this way, it's too dangerous.
  #options.repozo_opts.extend(getattr(module, 'repozo_opts', []))
  if options.port is None:
    options.port = 9001

  if options.host is None:
    usage(1, 'Either -H or --host is required (or host value should be set in configuration file).')

  return options

options = parseargs()
address = (options.host, options.port)
zope_formated_url = options.base_url
if options.base_url is not None and '%s' not in zope_formated_url:
  raise ValueError, 'Given base url (%r) is not properly formated, it must contain one \'%%s\'.' % (zope_formated_url, )
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
    check=options.dry_run)
else:
  repozo_formated_command += ' -f "%s" -m "%s"'
  result = backup(
    address=address,
    known_tid_storage_identifier_dict=options.known_tid_storage_identifier_dict,
    zope_formated_url=zope_formated_url,
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

sys.exit(result)
