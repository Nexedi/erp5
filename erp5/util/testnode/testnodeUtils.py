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

def generateRandomString(size):
  tab = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  
  my_string = ''
  for i in range(size):
    my_string = my_string + choice(tab)
  return my_string