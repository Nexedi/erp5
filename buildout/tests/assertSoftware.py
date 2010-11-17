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

import os
import subprocess
import unittest

def getCleanList(s):
  """Converts free form string separated by whitespaces to python list"""
  return sorted([q.strip() for q in s.split() if len(q.strip()) > 0])

def readElfAsDict(f):
  """Reads ELF information from file"""
  popen = subprocess.Popen(['readelf', '-d', os.path.join(*f.split('/'))],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  result = popen.communicate()[0]
  if popen.returncode != 0:
    raise AssertionError(result)
  library_list = []
  rpath_list = []
  runpath_list = []
  for l in result.split('\n'):
    if '(NEEDED)' in l:
      library_list.append(l.split(':')[1].strip(' []').split('.so')[0])
    elif '(RPATH)' in l:
      rpath_list = [q.rstrip('/') for q in l.split(':',1)[1].strip(' []').split(':')]
    elif '(RUNPATH)' in l:
      runpath_list = [q.rstrip('/') for q in l.split(':',1)[1].strip(' []').split(':')]
  if len(runpath_list) == 0:
    runpath_list = rpath_list
  elif len(rpath_list) != 0 and runpath_list != rpath_list:
    raise ValueError('RPATH and RUNPATH are different.')
  return dict(
    library_list=sorted(library_list),
    runpath_list=sorted(runpath_list)
  )

class AssertSoftwareMixin(unittest.TestCase):
  def assertEqual(self, first, second, msg=None):
    try:
      return unittest.TestCase.assertEqual(self, first, second, msg=msg)
    except unittest.TestCase.failureException:
      if (msg is None) and \
          isinstance(first, list) and \
          isinstance(second, list):
        msg = ''
        for elt in first:
          if elt not in second:
            msg += '- %s\n' % elt
        for elt in second:
          if elt not in first:
            msg += '+ %s\n' % elt
        if msg == '':
          raise
        else:
          msg = 'Lists are different:\n%s' % msg
          raise unittest.TestCase.failureException, msg
      else:
        raise

class AssertSoftwareRunable(AssertSoftwareMixin):
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

class AssertMysql50Tritonn(AssertSoftwareMixin):
  def test_ld_mysqld(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/libexec/mysqld')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libdl',
      'libgcc_s', 'libm', 'libnsl', 'libpthread', 'librt', 'libsenna',
      'libssl', 'libstdc++', 'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'senna', 'readline', 'openssl']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysqlmanager(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/libexec/mysqlmanager')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libgcc_s',
      'libm', 'libnsl', 'libpthread', 'libssl', 'libstdc++', 'libz']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_libmysqlclient_r(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/lib/mysql/libmysqlclient_r.so')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libm', 'libnsl',
      'libpthread', 'libssl', 'libz']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_libmysqlclient(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/lib/mysql/libmysqlclient.so')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libm', 'libnsl',
      'libssl', 'libz']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_sphinx(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/lib/mysql/sphinx.so')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libgcc_s', 'libm', 'libnsl',
      'libpthread', 'libstdc++']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysql(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/bin/mysql')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libgcc_s', 'libm',
      'libmysqlclient', 'libncurses', 'libnsl', 'libreadline', 'libssl', 'libstdc++',
      'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir),
      'parts', 'mysql-tritonn-5.0', 'lib', 'mysql'))
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysqladmin(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/bin/mysqladmin')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libgcc_s', 'libm',
      'libmysqlclient', 'libnsl', 'libssl', 'libstdc++', 'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir),
      'parts', 'mysql-tritonn-5.0', 'lib', 'mysql'))
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysqldump(self):
    elf_dict = readElfAsDict('parts/mysql-tritonn-5.0/bin/mysqldump')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libm',
      'libmysqlclient', 'libnsl', 'libssl', 'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline', 'openssl']]
    expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir),
      'parts', 'mysql-tritonn-5.0', 'lib', 'mysql'))
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertMysql51(AssertSoftwareMixin):
  def test_ld_mysqld(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/libexec/mysqld')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libdl', 'libgcc_s', 'libm', 'libnsl',
      'libpthread', 'libstdc++', 'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysqlmanager(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/libexec/mysqlmanager')
    self.assertEqual(sorted(['libc', 'libcrypt', 'libgcc_s', 'libm', 'libnsl',
      'libpthread', 'libstdc++', 'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_libmysqlclient_r(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/lib/mysql/libmysqlclient_r.so')
    self.assertEqual(sorted(['libc', 'libz', 'libcrypt', 'libm', 'libnsl', 'libpthread']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_libmysqlclient(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/lib/mysql/libmysqlclient.so')
    self.assertEqual(sorted(['libc', 'libz', 'libcrypt', 'libm', 'libnsl', 'libpthread']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'readline', 'zlib']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysql(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/bin/mysql')
    self.assertEqual(sorted(['libc', 'libz', 'libcrypt', 'libgcc_s', 'libm',
      'libmysqlclient', 'libncurses', 'libnsl', 'libpthread', 'libreadline',
      'libstdc++']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline']]
    expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir),
      'parts', 'mysql-5.1', 'lib', 'mysql'))
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysqladmin(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/bin/mysqladmin')
    self.assertEqual(sorted(['libc', 'libz', 'libcrypt', 'libgcc_s', 'libm',
      'libmysqlclient', 'libnsl', 'libpthread', 'libstdc++']),
      elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline']]
    expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir),
      'parts', 'mysql-5.1', 'lib', 'mysql'))
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_mysqldump(self):
    elf_dict = readElfAsDict('parts/mysql-5.1/bin/mysqldump')
    self.assertEqual(sorted(['libc', 'libz', 'libcrypt', 'libm', 'libmysqlclient',
      'libnsl', 'libpthread']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['ncurses', 'zlib', 'readline']]
    expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir),
      'parts', 'mysql-5.1', 'lib', 'mysql'))
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertMemcached(AssertSoftwareMixin):
  """Tests for built memcached"""

  def test_ld_memcached(self):
    """Checks proper linking to libevent from memcached"""
    elf_dict = readElfAsDict('parts/memcached/bin/memcached')
    self.assertEqual(sorted(['libpthread', 'libevent-1.4', 'libc']),
        elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['libevent']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertSubversion(AssertSoftwareMixin):
  """Tests for built subversion"""
  def test_ld_svn(self):
    elf_dict = readElfAsDict('parts/subversion/bin/svn')
    self.assertEqual(sorted(['libsvn_client-1', 'libsvn_wc-1', 'libsvn_ra-1',
      'libsvn_diff-1', 'libsvn_ra_local-1', 'libsvn_repos-1', 'libsvn_fs-1',
      'libsvn_fs_fs-1', 'libsvn_fs_util-1', 'libsvn_ra_svn-1',
      'libsvn_ra_neon-1', 'libsvn_delta-1', 'libsvn_subr-1', 'libsqlite3',
      'libaprutil-1', 'libapr-1', 'libuuid', 'librt', 'libneon', 'libexpat',
      'libz', 'libssl', 'libcrypto', 'libgssapi_krb5', 'libkrb5',
      'libk5crypto', 'libcom_err', 'libresolv', 'libc', 'libcrypt', 'libdl',
      'libpthread', 'libm', 'libserf-0', 'libsvn_ra_serf-1', 'libxml2'
      ]),
        elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['apache', 'libexpat', 'libxml2', 'neon', 'openssl',
                     'sqlite3', 'subversion', 'zlib', 'libuuid', 'serf']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertSerf(AssertSoftwareMixin):
  """Tests for built serf"""
  def test_ld_libserf(self):
    elf_dict = readElfAsDict('parts/serf/lib/libserf-0.so.0.0.0')
    self.assertEqual(sorted([
      'libapr-1', 'libaprutil-1', 'libc', 'libcrypt', 'libcrypto',
      'libdl', 'libexpat', 'libm', 'libpthread', 'librt',
      'libssl', 'libuuid', 'libz',
      ]),
        elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['apache', 'openssl', 'libexpat', 'libuuid', 'zlib']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertPythonMysql(AssertSoftwareMixin):
  def test_ld_mysqlso(self):
    for d in os.listdir('develop-eggs'):
      if d.startswith('MySQL_python'):
        path = os.path.join('develop-eggs', d, '_mysql.so')
        elf_dict = readElfAsDict(path)
        self.assertEqual(sorted(['libc', 'libcrypt', 'libcrypto', 'libm',
          'libmysqlclient_r', 'libnsl', 'libpthread', 'libssl', 'libz']),
          elf_dict['library_list'])
        soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
        expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
            software in ['zlib', 'openssl']]
        expected_rpath_list.append(os.path.join(os.path.abspath(os.curdir), 'parts', 'mysql-tritonn-5.0', 'lib', 'mysql'))
        self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertApache(AssertSoftwareMixin):
  """Tests for built apache"""

  def test_ld_libaprutil1(self):
    """Checks proper linking of libaprutil-1.so"""
    elf_dict = readElfAsDict('parts/apache/lib/libaprutil-1.so')
    self.assertEqual(sorted(['libexpat', 'libapr-1', 'librt', 'libcrypt',
      'libpthread', 'libdl', 'libc', 'libuuid']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['apache', 'zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_libapr1(self):
    """Checks proper linking of libapr-1.so"""
    elf_dict = readElfAsDict('parts/apache/lib/libapr-1.so')
    self.assertEqual(sorted(['librt', 'libcrypt', 'libuuid',
      'libpthread', 'libdl', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_modules(self):
    """Checks for availability of apache modules"""
    required_module_list = getCleanList("""
      actions_module
      alias_module
      asis_module
      auth_basic_module
      auth_digest_module
      authn_alias_module
      authn_anon_module
      authn_dbm_module
      authn_default_module
      authn_file_module
      authz_dbm_module
      authz_default_module
      authz_groupfile_module
      authz_host_module
      authz_owner_module
      authz_user_module
      autoindex_module
      bucketeer_module
      cache_module
      case_filter_in_module
      case_filter_module
      cern_meta_module
      cgi_module
      cgid_module
      charset_lite_module
      deflate_module
      dir_module
      disk_cache_module
      dumpio_module
      echo_module
      env_module
      expires_module
      ext_filter_module
      filter_module
      headers_module
      ident_module
      imagemap_module
      include_module
      info_module
      log_config_module
      log_forensic_module
      logio_module
      mime_magic_module
      mime_module
      negotiation_module
      optional_fn_export_module
      optional_fn_import_module
      optional_hook_export_module
      optional_hook_import_module
      proxy_balancer_module
      proxy_connect_module
      proxy_ftp_module
      proxy_http_module
      proxy_module
      rewrite_module
      setenvif_module
      speling_module
      ssl_module
      status_module
      substitute_module
      unique_id_module
      usertrack_module
      version_module
      vhost_alias_module
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

  def test_ld_module_mod_actions(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_actions.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_alias(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_alias.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_asis(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_asis.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_auth_basic(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_auth_basic.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_auth_digest(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_auth_digest.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authn_alias(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authn_alias.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authn_anon(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authn_anon.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authn_dbd(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authn_dbd.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authn_dbm(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authn_dbm.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authn_default(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authn_default.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authn_file(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authn_file.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authz_dbm(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authz_dbm.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authz_default(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authz_default.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authz_groupfile(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authz_groupfile.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authz_host(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authz_host.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authz_owner(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authz_owner.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_authz_user(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_authz_user.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_autoindex(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_autoindex.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_bucketeer(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_bucketeer.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_cache(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_cache.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_case_filter(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_case_filter.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_case_filter_in(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_case_filter_in.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_cern_meta(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_cern_meta.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_cgi(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_cgi.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_cgid(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_cgid.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_charset_lite(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_charset_lite.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_dav(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_dav.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_dav_fs(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_dav_fs.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_dbd(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_dbd.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_deflate(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_deflate.so')
    self.assertEqual(sorted(['libpthread', 'libc', 'libz']),
        elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_dir(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_dir.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_disk_cache(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_disk_cache.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_dumpio(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_dumpio.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_echo(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_echo.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_env(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_env.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_expires(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_expires.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_ext_filter(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_ext_filter.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_filter(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_filter.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_headers(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_headers.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_ident(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_ident.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_imagemap(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_imagemap.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_include(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_include.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_info(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_info.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_log_config(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_log_config.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_log_forensic(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_log_forensic.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_logio(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_logio.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_mime(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_mime.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_mime_magic(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_mime_magic.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_negotiation(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_negotiation.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_optional_fn_export(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_optional_fn_export.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_optional_fn_import(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_optional_fn_import.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_optional_hook_export(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_optional_hook_export.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_optional_hook_import(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_optional_hook_import.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy_ajp(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy_ajp.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy_balancer(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy_balancer.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy_connect(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy_connect.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy_ftp(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy_ftp.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy_http(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy_http.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_proxy_scgi(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_proxy_scgi.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_reqtimeout(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_reqtimeout.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_rewrite(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_rewrite.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_setenvif(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_setenvif.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_speling(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_speling.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_ssl(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_ssl.so')
    self.assertEqual(sorted(['libpthread', 'libc', 'libcrypto', 'libdl',
      'libssl', 'libz']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_status(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_status.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_substitute(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_substitute.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_unique_id(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_unique_id.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_userdir(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_userdir.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_usertrack(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_usertrack.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_version(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_version.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

  def test_ld_module_mod_vhost_alias(self):
    elf_dict = readElfAsDict('parts/apache/modules/mod_vhost_alias.so')
    self.assertEqual(sorted(['libpthread', 'libc']), elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['zlib', 'openssl', 'libuuid', 'libexpat', 'pcre']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

class AssertItools(AssertSoftwareMixin):
  def test_ld_parserso(self):
    elf_dict = readElfAsDict('parts/itools/lib/itools/xml/parser.so')
    self.assertEqual(sorted(['libc', 'libglib-2.0', 'libpthread']),
        elf_dict['library_list'])
    soft_dir = os.path.join(os.path.abspath(os.curdir), 'parts')
    expected_rpath_list = [os.path.join(soft_dir, software, 'lib') for
        software in ['glib']]
    self.assertEqual(sorted(expected_rpath_list), elf_dict['runpath_list'])

if __name__ == '__main__':
  unittest.main()
