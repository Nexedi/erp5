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
import pkg_resources
import slapos.slap
import subprocess
import time
import xml_marshaller
import shutil
import glob

MAX_PARTIONS = 10
MAX_SR_RETRIES = 3

def createFolder(folder, clean=False):
  if clean and os.path.exists(folder):
    shutil.rmtree(folder)
  if not(os.path.exists(folder)):
    os.mkdir(folder)

def createFolders(folder):
  if not(os.path.exists(folder)):
    os.makedirs(folder)

class SlapOSControler(object):

  def __init__(self, working_directory, config, log):
    self.config = config
    self.software_root = os.path.join(working_directory, 'soft')
    self.instance_root = os.path.join(working_directory, 'inst')
    self.slapos_config = os.path.join(working_directory, 'slapos.cfg')
    self.proxy_database = os.path.join(working_directory, 'proxy.db')
    self.log = log

  def _resetSoftware(self):
    self.log('SlapOSControler : GOING TO RESET ALL SOFTWARE : %r' %
             (self.software_root,))
    if os.path.exists(self.software_root):
      shutil.rmtree(self.software_root)
    os.mkdir(self.software_root)
    os.chmod(self.software_root, 0750)


  def initializeSlapOSControler(self, slapproxy_log=None, process_manager=None,
        reset_software=False, software_path_list=None):
    self.process_manager = process_manager
    self.software_path_list = software_path_list
    self.log('SlapOSControler, initialize, reset_software: %r' % reset_software)
    config = self.config
    slapos_config_dict = self.config.copy()
    slapos_config_dict.update(software_root=self.software_root,
                              instance_root=self.instance_root,
                              proxy_database=self.proxy_database)
    open(self.slapos_config, 'w').write(pkg_resources.resource_string(
         'erp5.util.testnode', 'template/slapos.cfg.in') %
           slapos_config_dict)
    createFolder(self.software_root)
    createFolder(self.instance_root)
    # By erasing everything, we make sure that we are able to "update"
    # existing profiles. This is quite dirty way to do updates...
    if os.path.exists(self.proxy_database):
      os.unlink(self.proxy_database)
    kwargs = dict(close_fds=True, preexec_fn=os.setsid)
    if slapproxy_log is not None:
      slapproxy_log_fp = open(slapproxy_log, 'w')
      kwargs['stdout'] = slapproxy_log_fp
      kwargs['stderr'] = slapproxy_log_fp
    proxy = subprocess.Popen([config['slapproxy_binary'],
      self.slapos_config], **kwargs)
    process_manager.process_pid_set.add(proxy.pid)
    # XXX: dirty, giving some time for proxy to being able to accept
    # connections
    time.sleep(10)
    slap = slapos.slap.slap()
    self.slap = slap
    self.slap.initializeConnection(config['master_url'])
    # register software profile
    for path in self.software_path_list:
      slap.registerSupply().supply(
          path,
          computer_guid=config['computer_id'])
    computer = slap.registerComputer(config['computer_id'])
    # Reset all previously generated software if needed
    if reset_software:
      self._resetSoftware()
    instance_root = self.instance_root
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
           'partition_list': [
             {'address_list': [{'addr': config['ipv4_address'],
                               'netmask': '255.255.255.255'},
                              {'addr': config['ipv6_address'],
                               'netmask': 'ffff:ffff:ffff::'},],
              'path': partition_path,
              'reference': partition_reference,
              'tap': {'name': partition_reference},}],
           'reference': config['computer_id'],
           'software_root': self.software_root}))

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
      status_dict = self.spawn(config['slapgrid_software_binary'],
                 '-v', '-c', '--all',
                 self.slapos_config, raise_error_if_fail=False,
                 log_prefix='slapgrid_sr', get_output=False)
      if status_dict['status_code'] == 0:
        break
    return status_dict

  def runComputerPartition(self, config, environment,
                           stdout=None, stderr=None):
    self.log("SlapOSControler.runComputerPartition")
    # cloudooo-json is required but this is a hack which should be removed
    config['instance_dict']['cloudooo-json'] = "{}"
    # report-url, report-project and suite-url are required to seleniumrunner
    # instance. This is a hack which must be removed.
    config['instance_dict']['report-url'] = config.get("report-url", "")
    config['instance_dict']['report-project'] = config.get("report-project", "")
    config['instance_dict']['suite-url'] = config.get("suite-url", "")
    for path in self.software_path_list:
      self.slap.registerOpenOrder().request(path,
        partition_reference='testing partition %s' % self.software_path_list.index(path),
        partition_parameter_kw=config['instance_dict'])

    # try to run for all partitions as one partition may in theory request another one 
    # this not always is required but curently no way to know how "tree" of partitions
    # may "expand"
    sleep_time = 0
    for runs in range(0, MAX_PARTIONS):
      status_dict = self.spawn(config['slapgrid_partition_binary'], '-v', '-c',
                 self.slapos_config, raise_error_if_fail=False,
                 log_prefix='slapgrid_cp', get_output=False)
      self.log('slapgrid_cp status_dict : %r' % (status_dict,))
      if status_dict['status_code'] in (0,):
        break
    # some hack to handle promise issues (should be only one of the two
    # codes, but depending on slapos versions, we have inconsistent status
    if status_dict['status_code'] in (1,2):
      status_dict['status_code'] = 0
    return status_dict
