##############################################################################
#
# Copyright (c) 2008-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Lukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
import sys, os, tempfile, stat, subprocess

def getCleanList(s):
  """Converts free form string separated by whitespaces to python list"""
  return sorted([q.strip() for q in s.split() if len(q.strip()) > 0])

def readElfAsDict(f):
  """Reads ELF information from file"""
  popen = subprocess.Popen(['readelf', '-d', f], stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)
  result = popen.communicate()[0]
  if popen.returncode != 0:
    return False
  library_list = []
  for l in result.split('\n'):
    if '(NEEDED)' in l:
      library_list.append(l.split(':')[1].strip(' []'))
    elif '(RPATH)' in l:
      rpath_list = l.split(':',1)[1].strip(' []').split(':')
    elif '(RUNPATH)' in l:
      runpath_list = l.split(':',1)[1].strip(' []').split(':')
  return dict(
    library_list=library_list,
    rpath_list=rpath_list,
    runpath_list=runpath_list
  )

class AssertPythonSoftware(unittest.TestCase):
  """Asserts that python related software is in good shape."""

  def test_python_version(self):
    """Check built python version"""
    self.assertEqual((2,4), sys.version_info[:2])

  def test_use_generated_python(self):
    """Checks generated python as python"""
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
      result = subprocess.Popen([name], stdout=subprocess.PIPE)\
          .communicate()[0].strip()
      self.assertEqual('(2, 4)', result)
    finally:
      os.unlink(name)

  def test_use_generated_python_as_normal_interpreter(self):
    """Checks behaviour of generated python as interpreter"""
    stdout, stderr = subprocess.Popen(["bin/python2.4", "-V"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertTrue('Python 2.4' in stderr)

  def test_required_libraries(self):
    """Checks possibility of importing libraries"""
    ignored_library_list = getCleanList("""
      socks
    """)
    required_library_list = getCleanList("""
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
      readline
      simplejson
      threadframe
      uuid
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
  """Checks for dynamic libraries"""

  def test_ocropus(self):
    """Ocropus"""
    result = os.system("ldd parts/ocropus/bin/ocropus | grep -q "
        "'parts/ocropus/lib/libocropus.so'")
    self.assertEqual(result, 0)
    result = os.system("ldd parts/ocropus/bin/ocropus | grep -q "
        "'parts/.*/lib/libiulib.so'")
    self.assertEqual(result, 0)

  def test_memcached_libevent(self):
    """Checks proper liunking to libevent from memcached"""
    result = os.system("ldd parts/memcached/bin/memcached | grep -q 'parts/li"
        "bevent/lib/libevent'")

class AssertSoftwareRunable(unittest.TestCase):
  def test_HaProxy(self):
    stdout, stderr = subprocess.Popen(["parts/haproxy/sbin/haproxy", "-v"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stderr, '')
    self.assertTrue(stdout.startswith('HA-Proxy'))

  def test_Apache(self):
    stdout, stderr = subprocess.Popen(["parts/apache/bin/httpd", "-v"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stderr, '')
    self.assertTrue(stdout.startswith('Server version: Apache'))

  def test_Varnish(self):
    stdout, stderr = subprocess.Popen(["parts/varnish/sbin/varnishd", "-V"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stdout, '')
    self.assertTrue(stderr.startswith('varnishd ('))

  def test_Ocropus(self):
    stdout, stderr = subprocess.Popen(["parts/ocropus/bin/ocropus"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stdout, '')
    self.assertTrue('splitting books' in stderr)

  def test_TokyoCabinet(self):
    stdout, stderr = subprocess.Popen(["parts/tokyocabinet/bin/tcamgr",
      "version"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stderr, '')
    self.assertTrue(stdout.startswith('Tokyo Cabinet'))

  def test_Flare(self):
    stdout, stderr = subprocess.Popen(["parts/flare/bin/flarei", "-v"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stderr, '')
    self.assertTrue(stdout.startswith('flare'))

  def test_rdiff_backup(self):
    stdout, stderr = subprocess.Popen(["bin/rdiff-backup", "-V"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stderr, '')
    self.assertEqual(stdout.strip(), 'rdiff-backup 1.0.5')

  def test_imagemagick(self):
    binary_list = [ 'animate', 'composite', 'convert', 'identify', 'mogrify',
        'stream', 'compare', 'conjure', 'display', 'import', 'montage']
    base = os.path.join('parts', 'imagemagick', 'bin')
    error_list = []
    for binary in binary_list:
      stdout, stderr = subprocess.Popen([os.path.join(base, binary), "-version"],
          stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
      if 'Version: ImageMagick' not in stdout:
        error_list.append(binary)
    self.assertEqual([], error_list)

  def test_w3m(self):
    stdout, stderr = subprocess.Popen(["parts/w3m/bin/w3m", "-V"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    self.assertEqual(stderr, '')
    self.assertTrue(stdout.startswith('w3m version w3m/0.5.2'))

  def test_MySQLdb(self):
    """Checks proper linking to mysql library from MySQLdb egg"""
    error_list = []
    for d in os.listdir('develop-eggs'):
      if d.startswith('MySQL_python'):
        path = os.path.join('develop-eggs', d, '_mysql.so')
        if os.system("ldd %s | grep -q 'parts/mysql-tritonn-5.0/lib/my"
            "sql/libmysqlclient_r.so'" % path) != 0:
          error_list.append(path)
    self.assertEqual(error_list, [])

class AssertMysql50Tritonn(unittest.TestCase):
  def test_tritonn_senna(self):
    """Senna as an library"""
    result = os.system("ldd parts/mysql-tritonn-5.0/libexec/mysqld | grep -q "
        "'parts/senna/lib/libsenna.so.0'")
    self.assertEqual(result, 0)

class AssertApache(unittest.TestCase):
  """Tests for built apache"""

  def test_ld_libaprutil1(self):
    """Checks proper linking"""
    elf_dict = readElfAsDict('parts/apache/lib/libaprutil-1.so')
    for lib in ['libexpat', 'libapr-1', 'librt',
        'libcrypt', 'libpthread', 'libdl', 'libc']:
      self.assertEqual(1, len([q for q in elf_dict['library_list'] if
        q.startswith(lib+'.')]), 'No %r found' % lib)

  def test_modules(self):
    """Checks for availability of apache modules"""
    required_module_list = getCleanList("""
      authn_default_module
      log_config_module
      proxy_http_module
      authn_alias_module
      authz_dbm_module
      case_filter_in_module
      imagemap_module
      setenvif_module
      include_module
      charset_lite_module
      info_module
      cache_module
      actions_module
      proxy_connect_module
      auth_digest_module
      unique_id_module
      mime_magic_module
      disk_cache_module
      mime_module
      usertrack_module
      asis_module
      optional_hook_import_module
      negotiation_module
      proxy_module
      authz_default_module
      ext_filter_module
      auth_basic_module
      authz_owner_module
      authn_anon_module
      rewrite_module
      proxy_balancer_module
      substitute_module
      filter_module
      expires_module
      autoindex_module
      status_module
      cgid_module
      version_module
      echo_module
      optional_fn_export_module
      optional_fn_import_module
      ident_module
      cgi_module
      bucketeer_module
      optional_hook_export_module
      vhost_alias_module
      ssl_module
      authz_user_module
      env_module
      logio_module
      proxy_ftp_module
      cern_meta_module
      authz_groupfile_module
      dir_module
      log_forensic_module
      alias_module
      deflate_module
      authn_dbm_module
      case_filter_module
      authz_host_module
      headers_module
      dumpio_module
      speling_module
      authn_file_module
    """)
    parts_path_prefix = os.path.join(os.path.dirname(__file__), '../parts')
    result = os.popen("%s/apache/bin/httpd -M" % parts_path_prefix)
    loaded_module_list = [module_name for module_name in result.read().split() 
                          if module_name.endswith('module')]
    result.close()
    failed_module_list = []
    for module in required_module_list:
      if module not in loaded_module_list:
        failed_module_list.append(module)
    self.assertEqual([], failed_module_list,
        'Apache modules not found:\n'+'\n'.join(failed_module_list))

if __name__ == '__main__':
  unittest.main()
