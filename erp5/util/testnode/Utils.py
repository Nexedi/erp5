import os
import stat
import shutil
import psutil
import logging

def rmtree(path):
  """Delete a path recursively.

  Like shutil.rmtree, but supporting the case that some files or folder
  might have been marked read only.  """
  def chmod_retry(func, path, _):
    """Make sure the file is writeable / the directory is executable.
    """
    if not os.path.exists(path):
      # because we are calling again rmtree on listdir errors, this path might
      # have been already deleted by the recursive call to rmtree.
      return

    os.chmod(path, 0o777)
    if func is os.listdir:
      # corner case to handle errors in listing directories.
      # https://bugs.python.org/issue8523
      # This might raises MaxRecursionError when the directory cannot be listed
      # for other reasons than "user does not have read permssion"
      return shutil.rmtree(path, onerror=chmod_retry)
    func(path)
  shutil.rmtree(path, onerror=chmod_retry)


def createFolder(folder, clean=False):
  if os.path.exists(folder):
    if not clean:
      return
    # before removing, check that we don't have a supervisord left here,
    # and refuse to erase this directory in that case.
    supervisord_pid_file = os.path.join(folder, 'var/run/supervisord.pid')
    if os.path.exists(supervisord_pid_file):
      with open(supervisord_pid_file, 'r') as f:
        pid = int(f.read().strip())
        supervisord = psutil.Process(pid)
        if supervisord.cmdline()[-1].endswith("supervisor.supervisord.main()"):
          logger = logging.getLogger()
          logger.error("Supervisord is already running in this directory ( pid: %s )", pid)
          # XXX terminate ?
          # supervisord.terminate()
          raise RuntimeError("Supervisord is already running")
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
