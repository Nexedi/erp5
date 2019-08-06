#!/usr/bin/env python

import sys
import requests

class Connection(object):
  def get(self, url):
    error_message_set = set()
    result = None
    try:
      response = requests.get(url, timeout=300)
      if response.status_code != 200:
        raise ValueError("response status %d" % response.status_code)
      result = response.text
    except Exception as e:
      error_message_set.add("Error: %s" % str(e))
      return result, error_message_set
    return result, error_message_set

def main():
  exit_status = 0
  error_message_set = set()
  if len(sys.argv) != 2:
    error_message_set.add("Error in parameters, please run : requestUrl [URL]")
  else:
    result, error_message_set = Connection().get(sys.argv[1])
  if error_message_set:
    exit_status = 1
    for error in error_message_set:
      print(error)
  elif result:
    print(result)
  sys.exit(exit_status)
