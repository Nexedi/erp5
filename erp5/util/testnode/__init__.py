##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
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
import ConfigParser
import argparse
import logging
import os
import pkg_resources

import testnode

CONFIG = dict(
  computer_id='COMPUTER',
  partition_reference='test0',
)

def main(*args):
  parser = argparse.ArgumentParser()
  parser.add_argument("configuration_file", nargs=1, type=argparse.FileType(),
      help="Configuration file.")
  parser.add_argument('-c', '--console', action='store_true',
      help="Enable console output.")
  parser.add_argument('-l', '--logfile', help="Enable output into logfile.")
  if args:
    parsed_argument = parser.parse_args(list(args))
  else:
    parsed_argument = parser.parse_args()
  logger = logging.getLogger('erp5testnode')
  if parsed_argument.console or parsed_argument.logfile:
    logger.setLevel(logging.INFO)
    if parsed_argument.console:
      logger.addHandler(logging.StreamHandler())
      logger.info('Activated console output.')
    if parsed_argument.logfile:
      logger.addHandler(logging.FileHandler(filename=parsed_argument.logfile))
      logger.info('Activated logfile %r output' % parsed_argument.logfile)
  else:
    logger.addHandler(logging.NullHandler())
  CONFIG['logger'] = logger.info
  config = ConfigParser.SafeConfigParser()
  # do not change case of option keys
  config.optionxform = str
  config.readfp(parsed_argument.configuration_file[0])
  def geto(o):
    return config.get('testnode', o)
  CONFIG['slapos_directory'] = geto('slapos_directory')
  CONFIG['working_directory'] = geto('working_directory')
  CONFIG['test_suite_directory'] = geto('test_suite_directory')
  CONFIG['log_directory'] = geto('log_directory')
  CONFIG['run_directory'] = geto('run_directory')
  for d in CONFIG['slapos_directory'], CONFIG['working_directory'], \
      CONFIG['test_suite_directory'], CONFIG['log_directory'], \
      CONFIG['run_directory']:
    if not os.path.isdir(d):
      raise ValueError('Directory %r does not exists.' % d)
  CONFIG['software_root'] = os.path.join(CONFIG['slapos_directory'],
        'software')
  CONFIG['instance_root'] = os.path.join(CONFIG['slapos_directory'],
        'instance')
  for d in CONFIG['software_root'], CONFIG['instance_root']:
    if not os.path.lexists(d):
      os.mkdir(d)
  CONFIG['proxy_database'] = os.path.join(CONFIG['slapos_directory'],
        'proxy.db')
  CONFIG['proxy_host'] = geto('proxy_host')
  CONFIG['proxy_port'] = geto('proxy_port')
  CONFIG['master_url'] = 'http://%s:%s' % (CONFIG['proxy_host'],
        CONFIG['proxy_port'])
  slapos_config = pkg_resources.resource_string('erp5.util.testnode',
    'template/slapos.cfg.in')
  slapos_config = slapos_config % CONFIG
  CONFIG['slapos_config'] = os.path.join(CONFIG['slapos_directory'],
    'slapos.cfg')
  open(CONFIG['slapos_config'], 'w').write(slapos_config)
  CONFIG['git_binary'] = geto('git_binary')
  CONFIG['zip_binary'] = geto('zip_binary')
  CONFIG['runTestSuite'] = os.path.join(CONFIG['instance_root'],
    CONFIG['partition_reference'], 'bin', 'runTestSuite')

  # generate vcs_repository_list
  vcs_repository_list = []
  for section in config.sections():
    if section.startswith('vcs_repository'):
      vcs_repository_list.append(dict(config.items(section)))

  CONFIG['bt5_path'] = None
  if 'bt5_path' in config.options("testnode"):
    bt5_path = config.get("testnode", 'bt5_path')
    if bt5_path.lower() != "none":
      CONFIG['bt5_path'] = bt5_path

  CONFIG['vcs_repository_list'] = vcs_repository_list
  CONFIG['test_suite_title'] = geto('test_suite_title')
  CONFIG['test_node_title'] = geto('test_node_title')
  CONFIG['test_suite'] = geto('test_suite')
  CONFIG['project_title'] = geto('project_title')
  CONFIG['node_quantity'] = geto('node_quantity')
  CONFIG['ipv4_address'] = geto('ipv4_address')
  CONFIG['ipv6_address'] = geto('ipv6_address')
  CONFIG['test_suite_master_url'] = geto('test_suite_master_url')
  CONFIG['slapgrid_partition_binary'] = geto('slapgrid_partition_binary')
  CONFIG['slapgrid_software_binary'] = geto('slapgrid_software_binary')
  bot_environment = {}
  if 'bot_environment' in config.sections():
    bot_environment = dict(config.items('bot_environment'))
  CONFIG['bot_environment'] = bot_environment
  CONFIG['environment'] = dict(config.items('environment'))
  CONFIG['slapproxy_binary'] = geto('slapproxy_binary')
  instance_dict = {}
  if 'instance_dict' in config.sections():
    instance_dict = dict(config.items('instance_dict'))
  CONFIG['instance_dict'] = instance_dict
  testnode.run(CONFIG)
