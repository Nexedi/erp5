##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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
from slapos.lib.recipe.BaseSlapRecipe import BaseSlapRecipe
import binascii
import os
import pkg_resources
import hashlib
import sys
import zc.buildout
import zc.recipe.egg

# global staic configuration parameters
CONFIG = dict(
  # Certificate Authority
  ca_prefix='ca',
  test_ca_prefix='test_ca',
  # Zope
  zope_user='zope',
  zope_port_base=12000,
  # Apache (login)
  login_apache_port_base=13000,
  # Apache (key login)
  key_auth_apache_port_base=14000,
  # MySQL
  mysql_database='erp5',
  mysql_port=45678,
  mysql_prefix='mysql',
  mysql_user='user',
  mysql_test_database='test_erp5',
  mysql_test_user='test_user',
  # Zeo
  zodb_data_prefix='zodb',
  zodb_root_filename='root.fs',
  zeo_port=22001,
  zeo_storagename='root',
  # HaProxy
  haproxy_login_port=15000,
  haproxy_key_auth_port=16000,
  # Memcached
  memcached_port=11000,
  # Kumofs
  kumo_manager_port=13101,
  kumo_server_port=13201,
  kumo_server_listen_port=13202,
  kumo_gateway_port=13301,
  # Conversion Server
  conversion_server_port=23000,
  conversion_server_ooo_port=23060,
)


# Taken from Zope2 egg
def write_inituser(fn, user, password):
  fp = open(fn, "w")
  pw = binascii.b2a_base64(hashlib.sha1(password).digest())[:-1]
  fp.write('%s:{SHA}%s\n' % (user, pw))
  fp.close()
  os.chmod(fn, 0600)


class Recipe(BaseSlapRecipe):
  def getTemplateFilename(self, template_name):
    return pkg_resources.resource_filename(__name__,
        'template/%s' % template_name)

  def _install(self):
    self.connection_dict = dict()
    self.path_list = []
    self.requirements, self.ws = self.egg.working_set([__name__])
    default_parameter_dict = dict(
      ca_country_code='XX',
      ca_email='xx@example.com',
      ca_state='State',
      ca_city='City',
      ca_company='Company',
      key_auth_path='/erp5/portal_slap'
      )
    for k, v in default_parameter_dict.iteritems():
      self.parameter_dict.setdefault(k, v)
    self.installMemcached()
    self.installKumo()
    self.installConversionServer()
    self.installMysqlServer()
    self.installERP5()
    zodb_dir = os.path.join(self.data_root_directory,
        CONFIG['zodb_data_prefix'])
    self._createDirectory(zodb_dir)
    CONFIG['zodb_root_path'] = os.path.join(zodb_dir,
                                            CONFIG['zodb_root_filename'])
    if 'zope_amount' in self.parameter_dict:
      simple_zope = False
      CONFIG['zope_amount'] = int(self.parameter_dict.get('zope_amount'))
    else:
      simple_zope = True
      CONFIG['zope_amount'] = 1
    if not simple_zope:
      self.installZeo()
    for zope_number in xrange(1, CONFIG['zope_amount'] + 1):
      self.installZope(zope_number, simple_zope)

    self.installERP5Site()
    self.installHaproxy()
    self.installTestRunner()
    self.linkBinary()
    self.computer_partition.setConnectionDict(self.connection_dict)
    return self.path_list

  def linkBinary(self):
    """Links binaries to instance's bin directory for easier exposal"""
    for linkline in self.options.get('link_binary_list', '').splitlines():
      if not linkline:
        continue
      target = linkline.split()
      if len(target) == 1:
        target = target[0]
        path, linkname = os.path.split(target)
      else:
        linkname = target[1]
        target = target[0]
      link = os.path.join(self.bin_directory, linkname)
      if os.path.lexists(link):
        if not os.path.islink(link):
          raise zc.buildout.UserError(
              'Target link already %r exists but it is not link' % link)
        os.unlink(link)
      os.symlink(target, link)
      self.logger.debug('Link %r -> %r created' % (link, target))
      self.path_list.append(link)

  def installKumo(self):
    ip = self.getLocalIPv4Address()
    CONFIG.update(
      kumo_gateway_binary=self.options['kumo_gateway_binary'],
      kumo_gateway_ip=ip,
      kumo_gateway_log=os.path.join(self.log_directory, "kumo-gateway.log"),
      kumo_manager_binary=self.options['kumo_manager_binary'],
      kumo_manager_ip=ip,
      kumo_manager_log=os.path.join(self.log_directory, "kumo-manager.log"),
      kumo_server_binary=self.options['kumo_server_binary'],
      kumo_server_ip=ip,
      kumo_server_log=os.path.join(self.log_directory, "kumo-server.log"),
      kumo_server_storage=os.path.join(self.data_root_directory, "kumodb.tch"),
    )

    self.path_list.append(self.createRunningWrapper('kumo_gateway',
      self.substituteTemplate(self.getTemplateFilename('kumo_gateway.in'),
        CONFIG)))

    self.path_list.append(self.createRunningWrapper('kumo_manager',
      self.substituteTemplate(self.getTemplateFilename('kumo_manager.in'),
        CONFIG)))

    self.path_list.append(self.createRunningWrapper('kumo_server',
      self.substituteTemplate(self.getTemplateFilename('kumo_server.in'),
        CONFIG)))

    self.connection_dict.update(
      kumo_manager_ip=CONFIG['kumo_manager_ip'],
      kumo_manager_port=CONFIG['kumo_manager_port'],
      kumo_server_ip=CONFIG['kumo_server_ip'],
      kumo_server_port=CONFIG['kumo_server_port'],
      kumo_gateway_ip=CONFIG['kumo_gateway_ip'],
      kumo_gateway_port=CONFIG['kumo_gateway_port'],
    )

  def installMemcached(self):
    CONFIG.update(
        memcached_binary=self.options['memcached_binary'],
        memcached_ip=self.getLocalIPv4Address())
    self.path_list.append(self.createRunningWrapper('memcached',
      self.substituteTemplate(self.getTemplateFilename('memcached.in'),
        CONFIG)))
    self.connection_dict.update(
      memcached_ip=CONFIG['memcached_ip'],
      memcached_port=CONFIG['memcached_port']
    )

  def installTestRunner(self):
    """Installs bin/runTestSuite executable to run all tests using
       bin/runUnitTest"""
    # XXX: This method can be drastically simplified after #20110128-1ECA63
    # (ERP5 specific runUnitTest script shall be generated by erp5 eggg) will
    # be solved
    testinstance = self.createDataDirectory('testinstance')
    # workaround wrong assumptions of ERP5Type.tests.runUnitTest about
    # directory existence
    unit_test = os.path.join(testinstance, 'unit_test')
    if not os.path.isdir(unit_test):
      os.mkdir(unit_test)
    runUnitTest = zc.buildout.easy_install.scripts([
      ('runUnitTest', __name__ + '.testrunner', 'runUnitTest')],
      self.ws, sys.executable, self.bin_directory, arguments=[dict(
        instance_home=testinstance,
        prepend_path=self.bin_directory,
        openssl_binary=self.options['openssl_binary'],
        test_ca_path=CONFIG['test_ca_path'],
        call_list=[self.options['runUnitTest_binary'],
          '--erp5_sql_connection_string', '%(mysql_test_database)s@%'
          '(mysql_ip)s:%(mysql_port)s %(mysql_test_user)s '
          '%(mysql_test_password)s' % self.connection_dict,
          '--conversion_server_hostname=%(conversion_server_ip)s' % \
                                                         self.connection_dict,
          '--conversion_server_port=%(conversion_server_port)s' % \
                                                         self.connection_dict
      ]
        )])[0]
    self.path_list.append(runUnitTest)

  def _installCertificateAuthority(self, prefix=''):
    CONFIG.update(
      ca_dir=os.path.join(self.data_root_directory,
                          CONFIG['%sca_prefix' % prefix]))
    CONFIG.update(
      ca_certificate=os.path.join(CONFIG['ca_dir'], 'cacert.pem'),
      ca_key=os.path.join(CONFIG['ca_dir'], 'private', 'cakey.pem'),
      ca_crl=os.path.join(CONFIG['ca_dir'], 'crl'),
      login_key=os.path.join(CONFIG['ca_dir'], 'private', 'login.key'),
      login_certificate=os.path.join(CONFIG['ca_dir'], 'certs',
        'login.crt'),
      key_auth_key=os.path.join(CONFIG['ca_dir'], 'private', 'keyauth.key'),
      key_auth_certificate=os.path.join(CONFIG['ca_dir'], 'certs',
        'keyauth.crt'),
    )
    self._createDirectory(CONFIG['ca_dir'])
    for d in ['certs', 'crl', 'newcerts', 'private']:
      self._createDirectory(os.path.join(CONFIG['ca_dir'], d))
    for f in ['crlnumber', 'serial']:
      if not os.path.exists(os.path.join(CONFIG['ca_dir'], f)):
        open(os.path.join(CONFIG['ca_dir'], f), 'w').write('01')
    if not os.path.exists(os.path.join(CONFIG['ca_dir'], 'index.txt')):
      open(os.path.join(CONFIG['ca_dir'], 'index.txt'), 'w').write('')
    ca_conf = CONFIG.copy()
    ca_conf['openssl_configuration'] = os.path.join(ca_conf['ca_dir'],
        'openssl.cnf')
    ca_conf.update(
        working_directory=CONFIG['ca_dir'],
        country_code=self.parameter_dict['ca_country_code'],
        state=self.parameter_dict['ca_state'],
        city=self.parameter_dict['ca_city'],
        company=self.parameter_dict['ca_company'],
        email_address=self.parameter_dict['ca_email'],
    )
    self._writeFile(ca_conf['openssl_configuration'],
        pkg_resources.resource_string(__name__,
          'template/openssl.cnf.ca.in') % ca_conf)
    self.path_list.extend(zc.buildout.easy_install.scripts([
      (prefix + 'certificate_authority',
        __name__ + '.certificate_authority', 'runCertificateAuthority')],
        self.ws, sys.executable, self.wrapper_directory, arguments=[dict(
          openssl_configuration=ca_conf['openssl_configuration'],
          openssl_binary=self.options['openssl_binary'],
          ca_certificate=os.path.join(CONFIG['ca_dir'], 'cacert.pem'),
          ca_key=os.path.join(CONFIG['ca_dir'], 'private', 'cakey.pem'),
          ca_crl=os.path.join(CONFIG['ca_dir'], 'crl'),
          login_key=os.path.join(CONFIG['ca_dir'], 'private', 'login.key'),
          login_certificate=os.path.join(CONFIG['ca_dir'], 'certs',
            'login.crt'),
          key_auth_key=os.path.join(CONFIG['ca_dir'], 'private',
            'keyauth.key'),
          key_auth_certificate=os.path.join(CONFIG['ca_dir'], 'certs',
            'keyauth.crt'),
          )]))
    self.connection_dict.update(
        openssl_binary=self.options['openssl_binary'],
        certificate_authority_path=CONFIG['ca_dir']
    )

  def installConversionServer(self):
    name = 'conversion_server'
    working_directory = self.createDataDirectory(name)
    conversion_server_dict = dict(
      working_path=working_directory,
      uno_path=self.options['ooo_uno_path'],
      office_binary_path=self.options['ooo_binary_path'],
      ip=self.getLocalIPv4Address(),
      port=CONFIG[name + '_port'],
      openoffice_port=CONFIG[name + '_ooo_port'],
    )
    for env_line in self.options['environment'].splitlines():
      env_line = env_line.strip()
      if not env_line:
        continue
      if '=' in env_line:
        env_key, env_value = env_line.split('=')
        conversion_server_dict[env_key.strip()] = env_value.strip()
      else:
        raise zc.buildout.UserError('Line %r in environment parameter is '
            'incorrect' % env_line)
    config_file = self.createConfigurationFile(name + '.cfg',
        self.substituteTemplate(self.getTemplateFilename('cloudooo.cfg.in'),
          conversion_server_dict))
    self.path_list.append(config_file)
    self.path_list.extend(zc.buildout.easy_install.scripts([(name,
      __name__ + '.execute', 'execute_with_signal_translation')], self.ws,
      sys.executable, self.wrapper_directory,
      arguments=[self.options['ooo_paster'].strip(), 'serve', config_file]))
    self.connection_dict.update(**{
      name + '_port': conversion_server_dict['port'],
      name + '_ip': conversion_server_dict['ip']
      })

  def installCertificateAuthority(self):
    self._installCertificateAuthority()

  def installTestCertificateAuthority(self):
    self._installCertificateAuthority('test_')
    CONFIG.update(
        test_ca_path=CONFIG['ca_dir']
    )

  def installHaproxy(self):
    listen_template = """listen %(name)s %(ip)s:%(port)s
  option ssl-hello-chk
  balance roundrobin
  %(server_list)s"""
    server_template = """server %(name)s %(address)s check"""

    ip_dict = dict(
        key_auth=self.getLocalIPv4Address(),
        login=self.getGlobalIPv6Address()
    )
    listen_list = []
    for key in ['key_auth', 'login']:
      conf = dict(
        name=key,
        ip=ip_dict[key],
        port=CONFIG['haproxy_%s_port' % key]
      )
      server_list = []
      for index in xrange(1, CONFIG['zope_amount'] + 1):
        k = '_'.join([key, str(index)])
        server_list.append(server_template % dict(name='_'.join([conf['name'],
          str(index)]),
          address=self.connection_dict[k]))
      conf['server_list'] = '\n  '.join(server_list)
      listen_list.append(listen_template % conf)
      key = 'haproxy_' + key + '_url'
      d = {key: '%(ip)s:%(port)s' % conf}
      CONFIG.update(**d)
      self.connection_dict.update(**d)
    haproxy_conf_path = self.createConfigurationFile('haproxy.cfg',
      self.substituteTemplate(self.getTemplateFilename('haproxy.cfg.in'),
        dict(listen_list='\n'.join(listen_list))))
    self.path_list.append(haproxy_conf_path)
    wrapper = zc.buildout.easy_install.scripts([('haproxy',
      __name__ + '.execute', 'execute')], self.ws, sys.executable,
      self.wrapper_directory, arguments=[
        self.options['haproxy_binary'].strip(), '-f', haproxy_conf_path]
      )[0]
    self.path_list.append(wrapper)

  def installERP5(self):
    """
    All zope have to share file created by portal_classes
    (until everything is integrated into the ZODB).
    So, do not request zope instance and create multiple in the same partition.
    """
    # Create instance directories
    self.erp5_directory = self.createDataDirectory('erp5shared')
    # Create init user
    password = self.generatePassword()
    write_inituser(os.path.join(self.erp5_directory, "inituser"),
        CONFIG['zope_user'], password)
    self.connection_dict.update(zope_user=CONFIG['zope_user'],
        zope_password=password)

    self._createDirectory(self.erp5_directory)
    for directory in (
      'Constraint',
      'Document',
      'Extensions',
      'PropertySheet',
      'import',
      'lib',
      'tests',
      'Products',
      ):
      self._createDirectory(os.path.join(self.erp5_directory, directory))
    return []

  def installERP5Site(self):
    """ Create a script controlled by supervisor, which creates a erp5
    site on current available zope and mysql environment"""
    mysql_connection_string = "%s@%s:%s %s %s" % (CONFIG['mysql_database'],
                                                  CONFIG['mysql_ip'],
                                                  CONFIG['mysql_port'],
                                                  CONFIG['mysql_user'],
                                                  CONFIG['mysql_password'])

    https_connection_url = "https://%s:%s@%s:%s/" % (CONFIG['zope_user'],
                                                     CONFIG['zope_password'],
                                                     self.backend_ip,
                                                     self.backend_port)

    self.path_list.extend(zc.buildout.easy_install.scripts([('erp5_update',
            __name__ + '.erp5', 'updateERP5')], self.ws,
                  sys.executable, self.wrapper_directory,
                  arguments=[mysql_connection_string, https_connection_url]))

    return []

  def installZeo(self):
    CONFIG.update(
      zeo_event_log=os.path.join(self.log_directory, 'zeo.log'),
      zeo_ip=self.getLocalIPv4Address(),
      zeo_zodb=CONFIG['zodb_root_path'],
      zeo_pid=os.path.join(self.run_directory, 'zeo.pid')
    )
    zeo_conf_path = self.createConfigurationFile('zeo.conf',
      self.substituteTemplate(self.getTemplateFilename('zeo.conf.in'), CONFIG))
    self.path_list.append(zeo_conf_path)
    wrapper = zc.buildout.easy_install.scripts([('zeo', __name__ + '.execute',
      'execute')], self.ws, sys.executable, self.wrapper_directory, arguments=[
        self.options['runzeo_binary'].strip(), '-C', zeo_conf_path]
      )[0]
    self.path_list.append(wrapper)

  def installZope(self, index, simple_zope):
    self.backend_ip = self.getLocalIPv4Address()
    self.backend_port = str(CONFIG['zope_port_base'] + index)
    # Create instance directories

    # Create zope configuration file
    zope_config = {}
    zope_config.update(self.options)
    zope_config.update(CONFIG)
    zope_config['instance'] = self.erp5_directory
    zope_config['event_log'] = os.path.join(self.log_directory,
        'zope_%s-event.log' % index)
    zope_config['z2_log'] = os.path.join(self.log_directory,
        'zope_%s-Z2.log' % index)
    zope_config['pid-filename'] = os.path.join(self.run_directory,
        'zope_%s.pid' % index)
    zope_config['lock-filename'] = os.path.join(self.run_directory,
        'zope_%s.lock' % index)

    prefixed_products = []
    for product in reversed(zope_config['products'].split()):
      product = product.strip()
      if product:
        prefixed_products.append('products %s' % product)
    prefixed_products.insert(0, 'products %s' % os.path.join(
                             self.erp5_directory, 'Products'))
    zope_config['products'] = '\n'.join(prefixed_products)
    zope_config['address'] = '%s:%s' % (self.backend_ip, self.backend_port)
    zope_config['tmp_directory'] = self.tmp_directory
    zope_config['path'] = ':'.join([self.bin_directory] +
        os.environ['PATH'].split(':'))

    if simple_zope:
      zope_wrapper_template_location = self.getTemplateFilename(
          'zope.conf.simple.in')
    else:
      zope_wrapper_template_location = self.getTemplateFilename('zope.conf.in')

    zope_conf_path = self.createConfigurationFile("zope_%s.conf" %
        index, self.substituteTemplate(
          zope_wrapper_template_location, zope_config))
    self.path_list.append(zope_conf_path)
    # Create init script
    wrapper = zc.buildout.easy_install.scripts([('zope_%s' % index,
      __name__ + '.execute', 'execute')], self.ws, sys.executable,
      self.wrapper_directory, arguments=[
        self.options['runzope_binary'].strip(), '-C', zope_conf_path]
      )[0]
    self.path_list.append(wrapper)

    self.installLoginApache(index)

  def _getApacheConfigurationDict(self, prefix, ip, port):
    apache_conf = dict()
    apache_conf['pid_file'] = os.path.join(self.run_directory,
        prefix + '.pid')
    apache_conf['lock_file'] = os.path.join(self.run_directory,
        prefix + '.lock')
    apache_conf['ip'] = ip
    apache_conf['port'] = port
    apache_conf['server_admin'] = 'admin@'
    apache_conf['error_log'] = os.path.join(self.log_directory,
        prefix + '-error.log')
    apache_conf['access_log'] = os.path.join(self.log_directory,
        prefix + '-access.log')
    return apache_conf

  def _writeApacheConfiguration(self, prefix, apache_conf):
    rewrite_rule_template = \
        "RewriteRule (.*) http://%(backend_ip)s:%(backend_port)s$1 [L,P]"
    path_template = pkg_resources.resource_string(__name__,
      'template/apache.zope.conf.path.in')
    path = path_template % dict(path='/')
    d = dict(
          path=path,
          backend_ip=self.backend_ip,
          backend_port=self.backend_port,
          backend_path='/',
          port=apache_conf['port'],
          vhname=path.replace('/', ''),
    )
    rewrite_rule = rewrite_rule_template % d
    apache_conf.update(**dict(
      path_enable=path,
      rewrite_rule=rewrite_rule
    ))
    return self.createConfigurationFile(prefix + '.conf',
        pkg_resources.resource_string(__name__,
          'template/apache.zope.conf.in') % apache_conf)

  def installLoginApache(self, index):
    ssl_template = """SSLEngine on
SSLCertificateFile %(login_certificate)s
SSLCertificateKeyFile %(login_key)s
SSLRandomSeed startup builtin
SSLRandomSeed connect builtin
"""
    apache_conf = self._getApacheConfigurationDict('login_apache_%s' % index,
        self.getLocalIPv4Address(), CONFIG['login_apache_port_base'] + index)
    apache_conf['server_name'] = '%s' % apache_conf['ip']
    apache_conf['ssl_snippet'] = ssl_template % CONFIG
    apache_config_file = self._writeApacheConfiguration('login_apache_%s' % \
      index, apache_conf)
    self.path_list.append(apache_config_file)
    self.path_list.extend(zc.buildout.easy_install.scripts([(
      'login_apache_%s' % index,
        __name__ + '.apache', 'runApache')], self.ws,
          sys.executable, self.wrapper_directory, arguments=[
            dict(
              required_path_list=[CONFIG['login_certificate'],
                CONFIG['login_key']],
              binary=self.options['httpd_binary'],
              config=apache_config_file
            )
          ]))
    self.connection_dict['login_%s' % index] = '%(ip)s:%(port)s' % apache_conf

  def installKeyAuthorisationApache(self, index):
    ssl_template = """SSLEngine on
SSLVerifyClient require
RequestHeader set REMOTE_USER %%{SSL_CLIENT_S_DN_CN}s
SSLCertificateFile %(key_auth_certificate)s
SSLCertificateKeyFile %(key_auth_key)s
SSLCACertificateFile %(ca_certificate)s
SSLCARevocationPath %(ca_crl)s"""
    apache_conf = self._getApacheConfigurationDict('key_auth_apache_%s' % \
        index,
        self.getLocalIPv4Address(),
        CONFIG['key_auth_apache_port_base'] + index)
    apache_conf['ssl_snippet'] = ssl_template % CONFIG
    prefix = 'ssl_key_auth_apache_%s' % index
    rewrite_rule_template = \
      "RewriteRule (.*) http://%(backend_ip)s:%(backend_port)s%(key_auth_path)s$1 [L,P]"
    path_template = pkg_resources.resource_string(__name__,
      'template/apache.zope.conf.path.in')
    path = path_template % dict(path='/')
    d = dict(
          path=path,
          backend_ip=self.backend_ip,
          backend_port=self.backend_port,
          backend_path='/',
          port=apache_conf['port'],
          vhname=path.replace('/', ''),
          key_auth_path=self.parameter_dict['key_auth_path'],
    )
    rewrite_rule = rewrite_rule_template % d
    apache_conf.update(**dict(
      path_enable=path,
      rewrite_rule=rewrite_rule
    ))
    apache_config_file = self.createConfigurationFile(prefix + '.conf',
        pkg_resources.resource_string(__name__,
          'template/apache.zope.conf.in') % apache_conf)
    self.path_list.append(apache_config_file)
    self.path_list.extend(zc.buildout.easy_install.scripts([(
      'key_auth_apache_%s' % index,
        __name__ + '.apache', 'runApache')], self.ws,
          sys.executable, self.wrapper_directory, arguments=[
            dict(
              required_path_list=[CONFIG['key_auth_certificate'],
                CONFIG['key_auth_key'], CONFIG['ca_certificate'],
                CONFIG['ca_crl']],
              binary=self.options['httpd_binary'],
              config=apache_config_file
            )
          ]))
    self.connection_dict['key_auth_%s' % index] = \
        '%(ip)s:%(port)s' % apache_conf

  def installMysqlServer(self):
    mysql_conf = dict(
        ip=self.getLocalIPv4Address(),
        data_directory=os.path.join(self.data_root_directory,
          CONFIG['mysql_prefix']),
        tcp_port=CONFIG['mysql_port'],
        pid_file=os.path.join(self.run_directory, 'mysqld.pid'),
        socket=os.path.join(self.run_directory, 'mysqld.sock'),
        error_log=os.path.join(self.log_directory, 'mysqld.log'),
        slow_query_log=os.path.join(self.log_directory,
        'mysql-slow.log'),
        mysql_database=CONFIG['mysql_database'],
        mysql_user=CONFIG['mysql_user'],
        mysql_password=self.generatePassword(),
        mysql_test_password=self.generatePassword(),
        mysql_test_database=CONFIG['mysql_test_database'],
        mysql_test_user=CONFIG['mysql_test_user'],
    )
    self._createDirectory(mysql_conf['data_directory'])

    mysql_conf_path = self.createConfigurationFile("my.cnf",
        self.substituteTemplate(self.getTemplateFilename('my.cnf.in'),
          mysql_conf))

    self.connection_dict.update(
        mysql_database=CONFIG['mysql_database'],
        mysql_ip=mysql_conf['ip'],
        mysql_password=mysql_conf['mysql_password'],
        mysql_port=CONFIG['mysql_port'],
        mysql_user=CONFIG['mysql_user'],
        mysql_test_database=CONFIG['mysql_test_database'],
        mysql_test_user=CONFIG['mysql_test_user'],
        mysql_test_password=mysql_conf['mysql_test_password'],
    )
    initialise_command_list = [self.options['mysql_install_binary'],
      '--skip-name-resolve', '--no-defaults',
      '--datadir=%s' % mysql_conf['data_directory']]
    mysql_command_list = [self.options['mysql_binary'].strip(),
        '--no-defaults', '-B', '--user=root',
        '--socket=%s' % mysql_conf['socket'],
        ]
    mysql_script = pkg_resources.resource_string(__name__,
        'template/initmysql.sql.in') % mysql_conf
    self.path_list.extend(zc.buildout.easy_install.scripts([('mysql_update',
      __name__ + '.mysql', 'updateMysql')], self.ws,
      sys.executable, self.wrapper_directory, arguments=[mysql_command_list,
        mysql_script]))
    self.path_list.extend(zc.buildout.easy_install.scripts([('mysqld',
      __name__ + '.mysql', 'runMysql')], self.ws,
        sys.executable, self.wrapper_directory, arguments=[
          initialise_command_list, {
        'mysqld_binary':self.options['mysqld_binary'],
        'configuration_file':mysql_conf_path,
        }]))
    self.path_list.extend([mysql_conf_path])
