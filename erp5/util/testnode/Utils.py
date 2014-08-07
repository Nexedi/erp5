import sys
import json
import shutil
import string
from random import choice

def deunicodeData(data):
  if isinstance(data, list):
    new_data = []
    for sub_data in data:
      new_data.append(deunicodeData(sub_data))
  elif isinstance(data, unicode):
    new_data = data.encode('utf8')
  elif isinstance(data, dict):
    new_data = {}
    for key, value in data.iteritems():
      key = deunicodeData(key)
      value = deunicodeData(value)
      new_data[key] = value
  else:
    new_data = data
  return new_data

def dealShebang(run_test_suite_path):
  line = open(run_test_suite_path, 'r').readline()
  invocation_list = []
  if line[:2] == '#!':
    invocation_list = line[2:].split()
  return invocation_list
