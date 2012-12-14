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

from testnode import TestNode

CONFIG = {
  'computer_id': 'COMPUTER',
  'partition_reference': 'test0',
}

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
  logger_format = '%(asctime)s %(name)-13s: %(levelname)-8s %(message)s'
  formatter = logging.Formatter(logger_format)
  logging.basicConfig(level=logging.INFO,
                     format=logger_format)
  logger = logging.getLogger('erp5testnode')
  if parsed_argument.console or parsed_argument.logfile:
    if parsed_argument.console:
      logger.addHandler(logging.StreamHandler())
      logger.info('Activated console output.')
    if parsed_argument.logfile:
      file_handler = logging.FileHandler(filename=parsed_argument.logfile)
      file_handler.setFormatter(formatter)
      logger.addHandler(file_handler)
      logger.info('Activated logfile %r output' % parsed_argument.logfile)
      CONFIG['log_file'] = parsed_argument.logfile
  else:
    logger.addHandler(logging.NullHandler())
  CONFIG['logger'] = logger.info
  config = ConfigParser.SafeConfigParser()
  # do not change case of option keys
  config.optionxform = str
  config.readfp(parsed_argument.configuration_file[0])
  for key in ('slapos_directory','working_directory','test_suite_directory',
              'log_directory','run_directory','proxy_host','proxy_port',
              'git_binary','zip_binary','node_quantity','test_node_title',
              'ipv4_address','ipv6_address','test_suite_master_url',
              'slapgrid_partition_binary','slapgrid_software_binary',
              'slapproxy_binary'):
    CONFIG[key] = config.get('testnode',key)

  for key in ('slapos_directory', 'working_directory', 'test_suite_directory',
      'log_directory', 'run_directory'):
    d = CONFIG[key]
    if not os.path.isdir(d):
      raise ValueError('Directory %r does not exists.' % d)
  CONFIG['master_url'] = 'http://%s:%s' % (CONFIG['proxy_host'],
        CONFIG['proxy_port'])

  # generate vcs_repository_list
  if 'bot_environment' in config.sections():
    bot_environment = dict(config.items('bot_environment'))
  else:
    bot_environment = {}
  CONFIG['bot_environment'] = bot_environment
  CONFIG['environment'] = dict(config.items('environment'))
  if 'instance_dict' in config.sections():
    instance_dict = dict(config.items('instance_dict'))
  else:
    instance_dict = {}
  CONFIG['instance_dict'] = instance_dict
  if 'software_list' in config.sections():
    CONFIG['software_list'] = filter(None,
        config.get("software_list", "path_list").split(","))

  testnode = TestNode(logger.info, CONFIG)
  testnode.run()
