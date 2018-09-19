import os
import stat
import shutil

def rmtree(path):
  """Delete a path recursively.

  Like shutil.rmtree, but supporting the case that some files or folder
  might have been marked read only.  """
  def chmod_retry(func, failed_path, _):
    """Make sure the file is writeable / the directory is executable.
    """
    if not os.path.exists(failed_path):
      # because we are calling again rmtree on listdir errors, this path might
      # have been already deleted by the recursive call to rmtree.
      return

    os.chmod(failed_path, 0o777)
    if func is os.listdir:
      # corner case to handle errors in listing directories.
      # https://bugs.python.org/issue8523
      # This might raises MaxRecursionError when the directory cannot be listed
      # for other reasons than "user does not have read permission"
      return shutil.rmtree(failed_path, onerror=chmod_retry)
    try:
      func(failed_path)
    except OSError:
      # if parent directory is not writable, we still cannot delete the file.
      if failed_path != path: # we don't want to change the parent of the folder we are deleting
        parent_folder = os.path.normpath(os.path.join(failed_path, '..'))
        os.chmod(parent_folder, 0o777)
      func(failed_path)

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
