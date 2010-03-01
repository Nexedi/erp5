import unittest
import sys, os, tempfile, stat, subprocess

def createCleanList(s):
  return sorted([q.strip() for q in s.split() if len(q.strip()) > 0])

class AssertPythonSoftware(unittest.TestCase):
  def test_python_version(self):
    self.assertEqual((2,4), sys.version_info[:2])

  def test_use_generated_python(self):
    fd, name = tempfile.mkstemp()
    try:
      f = os.fdopen(fd, 'w')
      f.write("""\
#!%s
import sys
print sys.version_info[:2]
    """ % sys.executable)
      f.close()
      f_stat = os.stat(name)
      os.chmod(name, f_stat.st_mode | stat.S_IXUSR)
      self.assertEqual(0, subprocess.call([name]))
    finally:
      os.unlink(name)

  def test_required_libraries(self):
    required_library_list = createCleanList("""
      ERP5Diff
      MySQLdb
      SOAPpy
      _ssl
      _xmlplus
      bz2
      cElementTree
      elementtree
      fpconst
      gdbm
      itools
      ldap
      lxml
      mechanize
      memcache
      numpy
      paramiko
      ply
      pytz
      simplejson
      socks
      threadframe
      xml
      xml.parsers.expat
      zlib
      """)
    failed_library_list = []
    for lib in required_library_list:
      try:
        __import__(lib)
      except ImportError:
        failed_library_list.append(lib)
    self.assertEqual([], failed_library_list,
        'Python libraries not found:\n'+'\n'.join(failed_library_list))

class AssertLddLibs(unittest.TestCase):
  def test_tritonn_senna(self):
    result = os.system("ldd parts/mysql-tritonn-5.0/libexec/mysqld | grep -q "
        "'parts/senna/lib/libsenna.so.0'")
    self.assertEqual(result, 0)

  def test_MySQLdb(self):
    result = os.system("ldd develop-eggs/MySQL_python-1.2.3c1-py2.4-linux-x86"
       "_64.egg/_mysql.so | grep -q 'parts/mysql-tritonn-5.0/lib/mysql/libmys"
       "qlclient_r.so'")
    self.assertEqual(result, 0)

  def test_memcached_libevent(self):
    result = os.system("ldd parts/memcached/bin/memcached | grep -q 'parts/li"
        "bevent/lib/libevent'")

class AssertApache(unittest.TestCase):
  def test_modules(self):
    required_module_list = createCleanList("""
      mod_authn_default.so
      mod_log_config.so
      mod_proxy_http.so
      mod_authn_alias.so
      mod_authz_dbm.so
      mod_case_filter_in.so
      mod_imagemap.so
      mod_setenvif.so
      mod_include.so
      mod_charset_lite.so
      mod_info.so
      mod_cache.so
      mod_actions.so
      mod_proxy_connect.so
      mod_auth_digest.so
      mod_unique_id.so
      mod_mime_magic.so
      mod_disk_cache.so
      mod_mime.so
      mod_usertrack.so
      mod_asis.so
      mod_optional_hook_import.so
      mod_negotiation.so
      mod_proxy.so
      mod_authz_default.so
      mod_ext_filter.so
      mod_auth_basic.so
      mod_authz_owner.so
      mod_authn_anon.so
      mod_rewrite.so
      mod_proxy_balancer.so
      mod_substitute.so
      mod_filter.so
      mod_expires.so
      mod_autoindex.so
      mod_status.so
      mod_cgid.so
      mod_version.so
      mod_echo.so
      mod_optional_fn_export.so
      mod_optional_fn_import.so
      mod_ident.so
      mod_cgi.so
      mod_bucketeer.so
      mod_optional_hook_export.so
      mod_vhost_alias.so
      mod_ssl.so
      mod_authz_user.so
      mod_env.so
      mod_logio.so
      mod_proxy_ftp.so
      mod_example.so
      mod_cern_meta.so
      mod_authz_groupfile.so
      mod_dir.so
      mod_log_forensic.so
      mod_alias.so
      mod_deflate.so
      mod_authn_dbm.so
      mod_case_filter.so
      mod_authz_host.so
      mod_headers.so
      mod_dumpio.so
      mod_speling.so
      mod_authn_file.so
    """)
    failed_module_list = []
    for module in required_module_list:
      if not os.path.exists('parts/apache/modules/%s' % module):
        failed_module_list.append(module)
    self.assertEqual([], failed_module_list,
        'Apache modules not found:\n'+'\n'.join(failed_module_list))

if __name__ == '__main__':
  unittest.main()
