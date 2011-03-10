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
  # MySQL
  mysql_database='erp5',
  mysql_port=45678,
  mysql_prefix='mysql',
  mysql_user='user',
  mysql_test_database='test_erp5',
  mysql_test_user='test_user',
  # Kumofs
  kumo_manager_port=13101,
  kumo_server_port=13201,
  kumo_server_listen_port=13202,
  kumo_gateway_port=13301,
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
    self.installTestCertificateAuthority()
    self.installCertificateAuthority()
    self.installMemcached(ip=self.getLocalIPv4Address(), port=11000)
    self.installKumo()
    self.installConversionServer(self.getLocalIPv4Address(), 23000, 23060)
    self.installMysqlServer()
    self.installERP5()
    zodb_dir = os.path.join(self.data_root_directory, 'zodb')
    self._createDirectory(zodb_dir)
    zodb_root_path = os.path.join(zodb_dir, 'root.fs')
    url_list = []
    if 'activity_node_amount' in self.parameter_dict or \
       'login_node_amount' in self.parameter_dict:
      self.zeo_address, self.zeo_storagename = self.installZeo(
          self.getLocalIPv4Address(), 22001, 'root', zodb_root_path)
      common_kw = dict(
          zeo_address=self.zeo_address,
          zeo_storagename=self.zeo_storagename,
          ip=self.getLocalIPv4Address())
      port = 12001
      distribution_list = [self.installZope(port=port, name='zope_distribution',
        with_timerservice=True, **common_kw)]
      activity_list = []
      for i in xrange(1, int(self.parameter_dict.get('activity_node_amount', 0)) + 1):
        port += 1
        activity_list.append(self.installZope(port=port, name='zope_activity_%s' % i,
          with_timerservice=True, **common_kw))
      login_list = []
      for i in xrange(1, int(self.parameter_dict.get('login_node_amount', 0)) + 1):
        port += 1
        login_list.append(self.installZope(port=port, name='zope_login_%s' % i,
          **common_kw))
      url_list = activity_list + login_list + distribution_list
    else:
      login_list = url_list
      url_list.append(self.installZope(ip=self.getLocalIPv4Address(),
          port=12000 + 1, name='zope_%s' % 1,
          zodb_root_path=CONFIG['zodb_root_path']))

    haproxy_login = self.installHaproxy(
          ip=self.getLocalIPv4Address(), port='15000', name='login',
          url_list=login_list, server_check_path=
          self.parameter_dict.get('server_check_path', '/erp5/getId'))
    self.connection_dict.update(
        apache_login=self.installLoginApache(ip=self.getGlobalIPv6Address(),
          port=13000, backend=haproxy_login))
    self.installTestRunner()
    self.linkBinary()
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
      self.logger.debug('Created link %r -> %r' % (link, target))
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
      kumo_address = '%s:%s' % (CONFIG['kumo_gateway_ip'],
        CONFIG['kumo_gateway_port'])
    )

  def installMemcached(self, ip, port):
    config = dict(
        memcached_binary=self.options['memcached_binary'],
        memcached_ip=ip,
        memcached_port=port,
    )
    self.path_list.append(self.createRunningWrapper('memcached',
      self.substituteTemplate(self.getTemplateFilename('memcached.in'),
        config)))
    self.connection_dict.update(memcached_url='%s:%s' %
        (config['memcached_ip'], config['memcached_port']))

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

  def installConversionServer(self, ip, port, openoffice_port):
    name = 'conversion_server'
    working_directory = self.createDataDirectory(name)
    conversion_server_dict = dict(
      working_path=working_directory,
      uno_path=self.options['ooo_uno_path'],
      office_binary_path=self.options['ooo_binary_path'],
      ip=ip,
      port=port,
      openoffice_port=openoffice_port,
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

  def installHaproxy(self, ip, port, name, server_check_path, url_list):
    server_template = """  server %(name)s %(address)s cookie %(name)s check inter 20s rise 2 fall 4"""
    config = dict(name=name, ip=ip, port=port,
        server_check_path=server_check_path,)
    i = 1
    server_list = []
    for url in url_list:
      server_list.append(server_template % dict(name='%s_%s' % (name, i),
        address=url))
      i += 1
    config['server_text'] = '\n'.join(server_list)
    haproxy_conf_path = self.createConfigurationFile('haproxy_%s.cfg' % name,
      self.substituteTemplate(self.getTemplateFilename('haproxy.cfg.in'),
        config))
    self.path_list.append(haproxy_conf_path)
    wrapper = zc.buildout.easy_install.scripts([('haproxy_%s' % name,
      __name__ + '.execute', 'execute')], self.ws, sys.executable,
      self.wrapper_directory, arguments=[
        self.options['haproxy_binary'].strip(), '-f', haproxy_conf_path]
      )[0]
    self.path_list.append(wrapper)
    return '%s:%s' % (ip, port)

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

  def installZeo(self, ip, port, name, path):
    config = dict(
      zeo_ip=ip,
      zeo_port=port,
      zeo_storagename=name,
      zeo_event_log=os.path.join(self.log_directory, 'zeo.log'),
      zeo_pid=os.path.join(self.run_directory, 'zeo.pid'),
      zeo_zodb=path
    )
    zeo_conf_path = self.createConfigurationFile('zeo.conf',
      self.substituteTemplate(self.getTemplateFilename('zeo.conf.in'), config))
    self.path_list.append(zeo_conf_path)
    wrapper = zc.buildout.easy_install.scripts([('zeo', __name__ + '.execute',
      'execute')], self.ws, sys.executable, self.wrapper_directory, arguments=[
        self.options['runzeo_binary'].strip(), '-C', zeo_conf_path]
      )[0]
    self.path_list.append(wrapper)
    return '%s:%s' % (config['zeo_ip'], config['zeo_port']), config['zeo_storagename']

  def installZope(self, ip, port, name, zeo_address=None, zeo_storagename=None,
      zodb_root_path=None, with_timerservice=False, timeserver_interval=5):
    # Create zope configuration file
    zope_config = dict(
        products=self.options['products'],
        timeserver_interval=timeserver_interval,
    )
    if zeo_address is not None and zeo_storagename is not None:
      zope_config.update(zeo_address=zeo_address, zeo_storagename=zeo_storagename)
    elif zodb_root_path is not None:
      zope_config.update(zodb_root_path=zodb_root_path)
    zope_config['instance'] = self.erp5_directory
    zope_config['event_log'] = os.path.join(self.log_directory,
        '%s-event.log' % name)
    zope_config['z2_log'] = os.path.join(self.log_directory,
        '%s-Z2.log' % name)
    zope_config['pid-filename'] = os.path.join(self.run_directory,
        '%s.pid' % name)
    zope_config['lock-filename'] = os.path.join(self.run_directory,
        '%s.lock' % name)

    prefixed_products = []
    for product in reversed(zope_config['products'].split()):
      product = product.strip()
      if product:
        prefixed_products.append('products %s' % product)
    prefixed_products.insert(0, 'products %s' % os.path.join(
                             self.erp5_directory, 'Products'))
    zope_config['products'] = '\n'.join(prefixed_products)
    zope_config['address'] = '%s:%s' % (ip, port)
    zope_config['tmp_directory'] = self.tmp_directory
    zope_config['path'] = ':'.join([self.bin_directory] +
        os.environ['PATH'].split(':'))

    if zeo_address is None:
      zope_wrapper_template_location = self.getTemplateFilename(
          'zope.conf.simple.in')
      with_timerservice = True
    else:
      zope_wrapper_template_location = self.getTemplateFilename('zope.conf.in')

    zope_conf_content = self.substituteTemplate(
        zope_wrapper_template_location, zope_config)
    if with_timerservice:
      zope_conf_content += self.substituteTemplate(
          self.getTemplateFilename('zope.conf.timerservice.in'), zope_config)
    zope_conf_path = self.createConfigurationFile("%s.conf" % name,
        zope_conf_content)
    self.path_list.append(zope_conf_path)
    # Create init script
    wrapper = zc.buildout.easy_install.scripts([(name,
      __name__ + '.execute', 'execute')], self.ws, sys.executable,
      self.wrapper_directory, arguments=[
        self.options['runzope_binary'].strip(), '-C', zope_conf_path]
      )[0]
    self.path_list.append(wrapper)
    return zope_config['address']

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

  def _writeApacheConfiguration(self, prefix, apache_conf, backend):
    rewrite_rule_template = \
        "RewriteRule (.*) http://%(backend)s$1 [L,P]"
    path_template = pkg_resources.resource_string(__name__,
      'template/apache.zope.conf.path.in')
    path = path_template % dict(path='/')
    d = dict(
          path=path,
          backend=backend,
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

  def installLoginApache(self, ip, port, backend):
    ssl_template = """SSLEngine on
SSLCertificateFile %(login_certificate)s
SSLCertificateKeyFile %(login_key)s
SSLRandomSeed startup builtin
SSLRandomSeed connect builtin
"""
    apache_conf = self._getApacheConfigurationDict('login_apache', ip, port)
    apache_conf['server_name'] = '%s' % apache_conf['ip']
    apache_conf['ssl_snippet'] = ssl_template % CONFIG
    apache_config_file = self._writeApacheConfiguration('login_apache',
        apache_conf, backend)
    self.path_list.append(apache_config_file)
    self.path_list.extend(zc.buildout.easy_install.scripts([(
      'login_apache',
        __name__ + '.apache', 'runApache')], self.ws,
          sys.executable, self.wrapper_directory, arguments=[
            dict(
              required_path_list=[CONFIG['login_certificate'],
                CONFIG['login_key']],
              binary=self.options['httpd_binary'],
              config=apache_config_file
            )
          ]))
    return 'https://%(ip)s:%(port)s' % apache_conf

  def installKeyAuthorisationApache(self, ip, port, backend):
    ssl_template = """SSLEngine on
SSLVerifyClient require
RequestHeader set REMOTE_USER %%{SSL_CLIENT_S_DN_CN}s
SSLCertificateFile %(key_auth_certificate)s
SSLCertificateKeyFile %(key_auth_key)s
SSLCACertificateFile %(ca_certificate)s
SSLCARevocationPath %(ca_crl)s"""
    apache_conf = self._getApacheConfigurationDict('key_auth_apache', ip, port)
    apache_conf['ssl_snippet'] = ssl_template % CONFIG
    prefix = 'ssl_key_auth_apache'
    rewrite_rule_template = \
      "RewriteRule (.*) http://%(backend)s%(key_auth_path)s$1 [L,P]"
    path_template = pkg_resources.resource_string(__name__,
      'template/apache.zope.conf.path.in')
    path = path_template % dict(path='/')
    d = dict(
          path=path,
          backend=backend,
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
      'key_auth_apache',
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
    return 'https://%(ip)s:%(port)s' % apache_conf

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
