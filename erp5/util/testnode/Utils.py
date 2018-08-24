import os
import stat
import shutil

def rmtree(path):
  """Delete a path recursively.

  Like shutil.rmtree, but supporting the case that some files or folder
  might have been marked read only.  """
  def chmod_retry(func, path, _):
    """Make sure the file is writeable / the directory is executable.
    """
    os.chmod(path, 0o777)
    func(path)
  shutil.rmtree(path, onerror=chmod_retry)


def createFolder(folder, clean=False):
  if os.path.exists(folder):
    if not clean:
      return
    rmtree(folder)
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
