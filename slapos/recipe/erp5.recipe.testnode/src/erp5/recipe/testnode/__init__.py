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
import os
import pkg_resources
import zc.buildout
import zc.recipe.egg
import sys

CONFIG = dict(
  proxy_port='5000',
  computer_id='COMPUTER',
  partition_reference='test0',
)

class Recipe(BaseSlapRecipe):
  def __init__(self, buildout, name, options):
    self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
    BaseSlapRecipe.__init__(self, buildout, name, options)

  def installSlapOs(self):
    CONFIG['slapos_directory'] = self.createDataDirectory('slapos')
    CONFIG['working_directory'] = self.createDataDirectory('testnode')
    CONFIG['software_root'] = os.path.join(CONFIG['slapos_directory'],
        'software')
    CONFIG['instance_root'] = os.path.join(CONFIG['slapos_directory'],
        'instance')
    CONFIG['proxy_database'] = os.path.join(CONFIG['slapos_directory'],
        'proxy.db')
    CONFIG['proxy_host'] = self.getLocalIPv4Address()
    CONFIG['master_url'] = 'http://%s:%s' % (CONFIG['proxy_host'],
        CONFIG['proxy_port'])
    self._createDirectory(CONFIG['software_root'])
    self._createDirectory(CONFIG['instance_root'])
    CONFIG['slapos_config'] = self.createConfigurationFile('slapos.cfg',
        self.substituteTemplate(pkg_resources.resource_filename(__name__,
          'template/slapos.cfg.in'), CONFIG))
    self.path_list.append(CONFIG['slapos_config'])

  def setupRunningWrapper(self):
    self.path_list.extend(zc.buildout.easy_install.scripts([(
      'testnode',
        __name__+'.testnode', 'run')], self.ws,
          sys.executable, self.wrapper_directory, arguments=[
            dict(
              computer_id=CONFIG['computer_id'],
              instance_dict=eval(self.parameter_dict.get('instance_dict', '{}')),
              instance_root=CONFIG['instance_root'],
              ipv4_address=self.getLocalIPv4Address(),
              ipv6_address=self.getGlobalIPv6Address(),
              master_url=CONFIG['master_url'],
              profile_path=self.parameter_dict['profile_path'],
              proxy_database=CONFIG['proxy_database'],
              proxy_port=CONFIG['proxy_port'],
              slapgrid_partition_binary=self.options['slapgrid_partition_binary'],
              slapgrid_software_binary=self.options['slapgrid_software_binary'],
              slapos_config=CONFIG['slapos_config'],
              slapproxy_binary=self.options['slapproxy_binary'],
              git_binary=self.options['git_binary'],
              software_root=CONFIG['software_root'],
              working_directory=CONFIG['working_directory'],
              vcs_repository=self.parameter_dict.get('vcs_repository'),
              node_quantity=self.parameter_dict.get('node_quantity', '1'),
              branch=self.parameter_dict.get('branch', None),
              test_suite_master_url=self.parameter_dict.get(
                                'test_suite_master_url', None),
              test_suite_name=self.parameter_dict.get('test_suite_name'),
              test_suite_title=self.parameter_dict.get('test_suite_title'),
              bin_directory=self.bin_directory,
              foo='bar',
              # botenvironemnt is splittable string of key=value to substitute
              # environment of running bot
              bot_environment=self.parameter_dict.get('bot_environment', ''),
              partition_reference=CONFIG['partition_reference'],
              environment=dict(PATH=os.environ['PATH']),
            )
          ]))

  def installLocalSvn(self):
    svn_dict = dict(svn_binary = self.options['svn_binary'])
    svn_dict.update(self.parameter_dict)
    self._writeExecutable(os.path.join(self.bin_directory, 'svn'), """\
#!/bin/sh
%(svn_binary)s --username %(svn_username)s --password %(svn_password)s \
--non-interactive --trust-server-cert --no-auth-cache "$@" """% svn_dict)

    svnversion = os.path.join(self.bin_directory, 'svnversion')
    if os.path.lexists(svnversion):
      os.unlink(svnversion)
    os.symlink(self.options['svnversion_binary'], svnversion)

  def installLocalGit(self):
    git_dict = dict(git_binary = self.options['git_binary'])
    git_dict.update(self.parameter_dict)
    double_slash_end_position = 1
    # XXX, this should be provided by slapos
    print "bin_directory : %r" % self.bin_directory
    home_directory = os.path.join(*os.path.split(self.bin_directory)[0:-1])
    print "home_directory : %r" % home_directory
    git_dict.setdefault("git_server_name", "git.erp5.org")
    if git_dict.get('vcs_username', None) is not None:
      netrc_file = open(os.path.join(home_directory, '.netrc'), 'w')
      netrc_file.write("""
  machine %(git_server_name)s
  login %(vcs_username)s
  password %(vcs_password)s""" % git_dict)
      netrc_file.close()

  def installLocalRepository(self):
    if self.parameter_dict.get('vcs_repository').endswith('git'):
      self.installLocalGit()
    else:
      self.installLocalSvn()

  def installLocalZip(self):
    zip = os.path.join(self.bin_directory, 'zip')
    if os.path.lexists(zip):
      os.unlink(zip)
    os.symlink(self.options['zip_binary'], zip)

  def installLocalPython(self):
    """Installs local python fully featured with eggs"""
    self.path_list.extend(zc.buildout.easy_install.scripts([], self.ws,
          sys.executable, self.bin_directory, scripts=None,
          interpreter='python'))

  def installLocalRunUnitTest(self):
    link = os.path.join(self.bin_directory, 'runUnitTest')
    destination = os.path.join(CONFIG['instance_root'],
        CONFIG['partition_reference'], 'bin', 'runUnitTest')
    if os.path.lexists(link):
      if not os.readlink(link) != destination:
        os.unlink(link)
    if not os.path.lexists(link):
      os.symlink(destination, link)

  def _install(self):
    self.requirements, self.ws = self.egg.working_set([__name__])
    self.path_list = []
    self.installSlapOs()
    self.setupRunningWrapper()
    self.installLocalRepository()
    self.installLocalZip()
    self.installLocalPython()
    self.installLocalRunUnitTest()
    return self.path_list
