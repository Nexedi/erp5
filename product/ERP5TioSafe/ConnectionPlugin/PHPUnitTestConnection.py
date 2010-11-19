import subprocess

class MethodWrapper(object):
  def __init__(self, method, conn):
    self._method = method
    self._conn = conn

  def __call__(self, *args, **kw):
    # build the php args and execute the php script
    php_args = ''
    for key, value in kw.items():
      php_args += '$_POST["%s"] = "%s";' % (key, value)
    php_args += 'include("%s/%s.php");' % (self._conn.url, self._method)
    process = subprocess.Popen(
        ['php', '-r', php_args, ],
        stdout=subprocess.PIPE,
    )
    return self._conn.url, process.stdout.read()

class PHPUnitTestConnection:
  """
    This is a unit test connection class which allows to execute a PHP script.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, url, user_name=None, password=None, credentials=None):
    """
      url (string)
        The requested url
      user_name (string or None)
      password (string is None)
        The transport-level (http) credentials to use.
      credentials (AuthenticationBase subclass instance or None)
        The interface-level (http) credentials to use.
    """
    self.url = url
    self._user_name = user_name
    self._password = password
    self._credentials = credentials

  def connect(self):
    """Get a handle to a remote connection."""
    return self

  def __getattr__(self, name):
    if not name.startswith("_"):
      return MethodWrapper(name, self)

