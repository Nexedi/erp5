import os
import stat
import shutil
import errno

import six
from six.moves import map

def rmtree(path):
  """Delete a path recursively.

  Like shutil.rmtree, but supporting the case that some files or folder
  might have been marked read only.  """
  def chmod_retry(func, failed_path, exc_info):
    """Make sure the directories are executable and writable.
    """
    # Depending on the Python version, the following items differ.
    if six.PY3:
      expected_error_type = PermissionError
      expected_func = os.lstat
    else:
      expected_error_type = OSError
      expected_func = os.listdir

    e = exc_info[1]
    if isinstance(e, expected_error_type):
      if e.errno == errno.ENOENT:
        # because we are calling again rmtree on listdir errors, this path might
        # have been already deleted by the recursive call to rmtree.
        return
      if e.errno == errno.EACCES:
        if func is expected_func:
          os.chmod(failed_path, 0o700)
          # corner case to handle errors in listing directories.
          # https://bugs.python.org/issue8523
          return shutil.rmtree(failed_path, onerror=chmod_retry)
        # If parent directory is not writable, we still cannot delete the file.
        # But make sure not to change the parent of the folder we are deleting.
        if failed_path != path:
          os.chmod(os.path.dirname(failed_path), 0o700)
          return func(failed_path)
    raise

  shutil.rmtree(path, onerror=chmod_retry)

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
