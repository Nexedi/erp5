import os
import six
from six.moves import map
from slapos.util import rmtree

def createFolder(folder, clean=False):
  if os.path.exists(folder):
    if not clean:
      return
    rmtree(folder)
  os.mkdir(folder)

if six.PY3:
  def deunicodeData(data):
    return data
else:
  def deunicodeData(data):
    if isinstance(data, list):
      return list(map(deunicodeData, data))
    if isinstance(data, unicode):
      return data.encode('utf8')
    if isinstance(data, dict):
      return {deunicodeData(key): deunicodeData(value)
              for key, value in six.iteritems(data)}
    return data
