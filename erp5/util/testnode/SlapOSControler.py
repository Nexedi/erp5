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
import os
import slapos.slap
import subprocess
import time
import xml_marshaller
import shutil

MAX_PARTIONS = 10
MAX_SR_RETRIES = 3

class SlapOSControler(object):

  def __init__(self, config, log,
      slapproxy_log=None, process_manager=None, reset_software=False):
    log('SlapOSControler, initialize, reset_software: %r' % reset_software)
    self.log = log
    self.config = config
    self.process_manager = process_manager
    # By erasing everything, we make sure that we are able to "update"
    # existing profiles. This is quite dirty way to do updates...
    if os.path.exists(config['proxy_database']):
      os.unlink(config['proxy_database'])
    kwargs = dict(close_fds=True, preexec_fn=os.setsid)
    if slapproxy_log is not None:
      slapproxy_log_fp = open(slapproxy_log, 'w')
      kwargs['stdout'] = slapproxy_log_fp
      kwargs['stderr'] = slapproxy_log_fp
    proxy = subprocess.Popen([config['slapproxy_binary'],
      config['slapos_config']], **kwargs)
    process_manager.process_pid_set.add(proxy.pid)
    # XXX: dirty, giving some time for proxy to being able to accept
    # connections
    time.sleep(10)
    slap = slapos.slap.slap()
    self.slap = slap
    self.slap.initializeConnection(config['master_url'])
    # register software profile
    self.software_profile = config['custom_profile_path']
    slap.registerSupply().supply(
        self.software_profile,
        computer_guid=config['computer_id'])
    computer = slap.registerComputer(config['computer_id'])
    # Reset all previously generated software if needed
    if reset_software:
      software_root = config['software_root']
      log('SlapOSControler : GOING TO RESET ALL SOFTWARE')
      if os.path.exists(software_root):
        shutil.rmtree(software_root)
      os.mkdir(software_root)
      os.chmod(software_root, 0750)
    instance_root = config['instance_root']
    if os.path.exists(instance_root):
      # delete old paritions which may exists in order to not get its data
      # (ex. MySQL db content) from previous testnode's runs
      # In order to be able to change partition naming scheme, do this at
      # instance_root level (such change happened already, causing problems).
      shutil.rmtree(instance_root)
    if not(os.path.exists(instance_root)):
      os.mkdir(instance_root)
    for i in range(0, MAX_PARTIONS):
      # create partition and configure computer
      # XXX: at the moment all partitions do share same virtual interface address
      # this is not a problem as usually all services are on different ports
      partition_reference = '%s-%s' %(config['partition_reference'], i)
      partition_path = os.path.join(instance_root, partition_reference)
      if not(os.path.exists(partition_path)):
        os.mkdir(partition_path)
      os.chmod(partition_path, 0750)
      computer.updateConfiguration(xml_marshaller.xml_marshaller.dumps({
                                                    'address': config['ipv4_address'],
                                                    'instance_root': instance_root,
                                                    'netmask': '255.255.255.255',
                                                    'partition_list': [{'address_list': [{'addr': config['ipv4_address'],
                                                                        'netmask': '255.255.255.255'},
                                                                       {'addr': config['ipv6_address'],
                                                                        'netmask': 'ffff:ffff:ffff::'},],
                                                    'path': partition_path,
                                                    'reference': partition_reference,
                                                    'tap': {'name': partition_reference},
                                                    }
                                                    ],
                                    'reference': config['computer_id'],
                                    'software_root': config['software_root']}))

  def spawn(self, *args, **kw):
    return self.process_manager.spawn(*args, **kw)

  def runSoftwareRelease(self, config, environment):
    self.log("SlapOSControler.runSoftwareRelease")
    cpu_count = os.sysconf("SC_NPROCESSORS_ONLN")
    os.putenv('MAKEFLAGS', '-j%s' % cpu_count)
    os.environ['PATH'] = environment['PATH']
    # a SR may fail for number of reasons (incl. network failures)
    # so be tolerant and run it a few times before giving up
    for runs in range(0, MAX_SR_RETRIES):
      status_dict = self.spawn(config['slapgrid_software_binary'], '-v', '-c',
                 config['slapos_config'], raise_error_if_fail=False,
                 log_prefix='slapgrid_sr', get_output=False)
    return status_dict

  def runComputerPartition(self, config, environment,
                           stdout=None, stderr=None):
    self.log("SlapOSControler.runComputerPartition")
    # cloudooo-json is required but this is a hack which should be removed
    config['instance_dict']['cloudooo-json'] = "{}"
    self.slap.registerOpenOrder().request(self.software_profile,
        partition_reference='testing partition',
        partition_parameter_kw=config['instance_dict'])

    # try to run for all partitions as one partition may in theory request another one 
    # this not always is required but curently no way to know how "tree" of partitions
    # may "expand"
    for runs in range(0, MAX_PARTIONS):
      status_dict = self.spawn(config['slapgrid_partition_binary'], '-v', '-c',
                 config['slapos_config'], raise_error_if_fail=False,
                 log_prefix='slapgrid_cp', get_output=False)
      self.log('slapgrid_cp status_dict : %r' % (status_dict,))
    return status_dict
