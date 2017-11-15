import os
import shutil

def createFolder(folder, clean=False):
  if os.path.exists(folder):
    if not clean:
      return
    shutil.rmtree(folder)
  os.mkdir(folder)

def deunicodeData(data):
  if isinstance(data, list):
    return map(deunicodeData, data)
  if isinstance(data, unicode):
    return data.encode('utf8')
  if isinstance(data, dict):
    return {deunicodeData(key): deunicodeData(value)
            for key, value in data.iteritems()}
  return data
