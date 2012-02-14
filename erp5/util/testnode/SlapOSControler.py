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

MAX_PARTIONS = 10
MAX_SR_RETRIES = 3

class SlapOSControler(object):

  def __init__(self, config, log, process_group_pid_set=None,
      slapproxy_log=None):
    self.log = log
    self.config = config
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
    process_group_pid_set.add(proxy.pid)
    # XXX: dirty, giving some time for proxy to being able to accept
    # connections
    time.sleep(10)
    slap = slapos.slap.slap()
    slap.initializeConnection(config['master_url'])
    # register software profile
    self.software_profile = config['custom_profile_path']
    slap.registerSupply().supply(
        self.software_profile,
        computer_guid=config['computer_id'])
    computer = slap.registerComputer(config['computer_id'])
    for i in range(0, MAX_PARTIONS):
      # create partition and configure computer
      # XXX: at the moment all partitions do share same virtual interface address
      # this is not a problem as usually all services are on different ports
      partition_reference = '%s-%s' %(config['partition_reference'], i)
      partition_path = os.path.join(config['instance_root'], partition_reference)
      if not os.path.exists(partition_path):
        os.mkdir(partition_path)
      os.chmod(partition_path, 0750)
      computer.updateConfiguration(xml_marshaller.xml_marshaller.dumps({
                                                    'address': config['ipv4_address'],
                                                    'instance_root': config['instance_root'],
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

  def runSoftwareRelease(self, config, environment, process_group_pid_set=None,
                         stdout=None, stderr=None):
    self.log("SlapOSControler.runSoftwareRelease")
    cpu_count = os.sysconf("SC_NPROCESSORS_ONLN")
    os.putenv('MAKEFLAGS', '-j%s' % cpu_count)
    os.environ['PATH'] = environment['PATH']
    command = [config['slapgrid_software_binary'], '-v', '-c',
      #'--buildout-parameter',"'-U -N' -o",
      config['slapos_config']]
    # a SR may fail for number of reasons (incl. network failures)
    # so be tolerant and run it a few times before giving up
    for runs in range(0, MAX_SR_RETRIES):
      slapgrid = subprocess.Popen(command,
        stdout=stdout, stderr=stderr,
        close_fds=True, preexec_fn=os.setsid)
      process_group_pid_set.add(slapgrid.pid)
      slapgrid.wait()

    stdout.seek(0)
    stderr.seek(0)
    process_group_pid_set.remove(slapgrid.pid)
    status_dict = {'status_code':slapgrid.returncode,
                    'command': repr(command),
                    'stdout':stdout.read(),
                    'stderr':stderr.read()}
    stdout.close()
    stderr.close()
    return status_dict

  def runComputerPartition(self, config, environment,
                           process_group_pid_set=None,
                           stdout=None, stderr=None):
    self.log("SlapOSControler.runComputerPartition")
    slap = slapos.slap.slap()
    # cloudooo-json is required but this is a hack which should be removed
    config['instance_dict']['cloudooo-json'] = "{}"
    slap.registerOpenOrder().request(self.software_profile,
        partition_reference='testing partition',
        partition_parameter_kw=config['instance_dict'])
    command = [config['slapgrid_partition_binary'],
      config['slapos_config'], '-c', '-v']

    # try to run for all partitions as one partition may in theory request another one 
    # this not always is required but curently no way to know how "tree" of partitions
    # may "expand"
    for runs in range(0, MAX_PARTIONS):
      slapgrid = subprocess.Popen(command,
        stdout=stdout, stderr=stderr,
        close_fds=True, preexec_fn=os.setsid)
      process_group_pid_set.add(slapgrid.pid)
      slapgrid.wait()
      process_group_pid_set.remove(slapgrid.pid)

    stdout.seek(0)
    stderr.seek(0)
    status_dict = {'status_code':slapgrid.returncode,
                    'command': repr(command),
                    'stdout':stdout.read(),
                    'stderr':stderr.read()}
    stdout.close()
    stderr.close()
    return status_dict
