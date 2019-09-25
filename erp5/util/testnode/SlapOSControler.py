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
import argparse
from slapos import client
from . import logger
from .Utils import createFolder

from six.moves import range

MAX_PARTITIONS = 10
MAX_SR_RETRIES = 3

class SlapOSControler(object):

  def __init__(self, working_directory, config, use_local_shared_part=False):
    self.config = config
    self.software_root = os.path.join(working_directory, 'soft')
    self.shared_part_list = [
        path.strip() for path in config['shared_part_list'].splitlines()
    ]
    if use_local_shared_part:
      shared = os.path.join(working_directory, 'shared')
      createFolder(shared)
      self.shared_part_list = self.shared_part_list + [shared]

    self.instance_root = os.path.join(working_directory, 'inst')
    self.slapos_config = os.path.join(working_directory, 'slapos.cfg')
    self.proxy_database = os.path.join(working_directory, 'proxy.db')
    self.instance_config = {}

  #TODO: implement a method to get all instance related the slapOS account
  # and deleting all old instances (based on creation date or name etc...)

  def createSlaposConfigurationFileAccount(self, key, certificate, slapos_url, config):
    # Create "slapos_account" directory in the "slapos_directory"
    slapos_account_directory = os.path.join(config['slapos_directory'], "slapos_account")
    createFolder(slapos_account_directory)
    # Create slapos-account files
    slapos_account_key_path = os.path.join(slapos_account_directory, "key")
    slapos_account_certificate_path = os.path.join(slapos_account_directory, "certificate")
    configuration_file_path = os.path.join(slapos_account_directory, "slapos.cfg")
    configuration_file_value = "[slapos]\nmaster_url = %s\n\
[slapconsole]\ncert_file = %s\nkey_file = %s" %(
                                  slapos_url,
                                  slapos_account_certificate_path,
                                  slapos_account_key_path)
    with open(slapos_account_key_path, "w") as f:
      f.write(key)
    with open(slapos_account_certificate_path, "w") as f:
      f.write(certificate)
    with open(configuration_file_path, "w") as f:
      f.write(configuration_file_value)
    self.configuration_file_path = configuration_file_path
    return slapos_account_key_path, slapos_account_certificate_path, configuration_file_path

  def supply(self, software_url, computer_id, state="available"):
    """
    Request the installation of a software release on a specific node
    Ex :
    my_controler.supply('kvm.cfg', 'COMP-726')
    """
    logger.debug('SlapOSControler : supply')
    parser = argparse.ArgumentParser()
    parser.add_argument("configuration_file")
    parser.add_argument("software_url")
    parser.add_argument("node")
    if os.path.exists(self.configuration_file_path):
      args = parser.parse_args([self.configuration_file_path, software_url, computer_id])
      config = client.Config()
      config.setConfig(args, args.configuration_file)
      try:
        local = client.init(config)
        local['supply'](software_url, computer_guid=computer_id, state=state)
        logger.debug('SlapOSControler: supply %s %s %s', software_url, computer_id, state)
      except Exception:
        logger.exception("SlapOSControler.supply")
        raise ValueError("Unable to supply (or remove)")
    else:
      raise ValueError("Configuration file not found.")

  def request(self, reference, software_url, software_type=None,
            software_configuration=None, computer_guid=None, state='started'):
    """
    configuration_file_path (slapos acount)
    reference : instance title
    software_url : software path/url
    software_type : scalability
    software_configuration : dict { "_" : "{'toto' : 'titi'}" } 

    Ex :
    my_controler._request('Instance16h34Ben',
                               'kvm.cfg', 'cluster', { "_" : "{'toto' : 'titi'}" } )

    """
    logger.debug('SlapOSControler : request-->SlapOSMaster')
    current_intance_config = {'software_type':software_type,
                              'software_configuration':software_configuration,
                              'computer_guid':computer_guid,
                              'software_url':software_url,
                              'requested_state':state,
                              'partition':None
                              }
    self.instance_config[reference] = current_intance_config

    filter_kw = None
    if computer_guid != None:
      filter_kw = { "computer_guid": computer_guid }
    if os.path.exists(self.configuration_file_path):
      parser = argparse.ArgumentParser()
      parser.add_argument("configuration_file")
      args = parser.parse_args([self.configuration_file_path])
      config = client.Config()
      config.setConfig(args, args.configuration_file)
      try:
        local = client.init(config)
        partition = local['request'](
          software_release = software_url,
          partition_reference = reference,
          partition_parameter_kw = software_configuration,
          software_type = software_type,
          filter_kw = filter_kw,
          state = state)
        self.instance_config[reference]['partition'] = partition
        if state == 'destroyed':
          del self.instance_config[reference]
        elif state == 'started':
          logger.debug('Instance started with configuration: %s',
                   software_configuration)
      except Exception:
        logger.exception("SlapOSControler.request")
        raise ValueError("Unable to do this request")
    else:
      raise ValueError("Configuration file not found.")

  def _requestSpecificState(self, reference, state):
    self.request(reference,
        self.instance_config[reference]['software_url'],
        self.instance_config[reference]['software_type'],
        self.instance_config[reference]['software_configuration'],
        self.instance_config[reference]['computer_guid'],
        state=state
    )    
  
  def destroyInstance(self, reference):
    logger.debug('SlapOSControler : delete instance')
    try:
      self._requestSpecificState(reference, 'destroyed')
    except Exception:
      raise ValueError("Can't delete instance %r (instance not created?)" % reference)
    
  def stopInstance(self, reference):
    logger.debug('SlapOSControler : stop instance')
    try:
      self._requestSpecificState(reference, 'stopped')
    except Exception:
      raise ValueError("Can't stop instance %r (instance not created?)" % reference)
  
  def startInstance(self, reference):
    logger.debug('SlapOSControler : start instance')
    try:
      self._requestSpecificState(reference, 'started')
    except Exception:
      raise ValueError("Can't start instance %r (instance not created?)" % reference)

  def updateInstanceXML(self, reference, software_configuration):
    """
    Update the XML configuration of an instance
    # Request same instance with different parameters.
    """
    logger.debug('SlapOSControler : updateInstanceXML will request same'
                 ' instance with new XML configuration...')

    try:
      self.request(reference,
        self.instance_config[reference]['software_url'],
        self.instance_config[reference]['software_type'],
        software_configuration,
        self.instance_config[reference]['computer_guid'],
        state='started'
      )
    except Exception:
      raise ValueError("Can't update instance '%s' (may not exist?)" %reference)

  def _resetSoftware(self):
    logger.info('SlapOSControler: GOING TO RESET ALL SOFTWARE : %r',
             self.software_root)
    createFolder(self.software_root, True)

  def initializeSlapOSControler(self, slapproxy_log=None, process_manager=None,
              reset_software=False, software_path_list=None):
    self.process_manager = process_manager
    self.software_path_list = software_path_list
    logger.debug('SlapOSControler, initialize, reset_software: %r', reset_software)
    config = self.config
    slapos_config_dict = config.copy()
    slapos_config_dict.update(software_root=self.software_root,
                              instance_root=self.instance_root,
                              proxy_database=self.proxy_database,
                              shared_part_list='\n  '.join(self.shared_part_list))

    with open(self.slapos_config, 'w') as f:
      f.write(pkg_resources.resource_string(
         'erp5.util.testnode', 'template/slapos.cfg.in') %
           slapos_config_dict)
    # By erasing everything, we make sure that we are able to "update"
    # existing profiles. This is quite dirty way to do updates...
    if os.path.exists(self.proxy_database):
      os.unlink(self.proxy_database)
    kwargs = dict(close_fds=True, preexec_fn=os.setsid)
    if slapproxy_log is not None:
      slapproxy_log_fp = open(slapproxy_log, 'w')
      kwargs['stdout'] = slapproxy_log_fp
      kwargs['stderr'] = slapproxy_log_fp
    proxy = subprocess.Popen([config['slapos_binary'], 
      'proxy', 'start', '--cfg' , self.slapos_config], **kwargs)
    process_manager.process_pid_set.add(proxy.pid)

    slap = self.slap = slapos.slap.slap()
    # Wait for proxy to accept connections
    retries = 0
    while True:
      time.sleep(1)
      try:
        slap.initializeConnection(config['master_url'])
        computer = slap.registerComputer(config['computer_id'])
        # Call a method to ensure connection to master can be established
        computer.getComputerPartitionList()
      except slapos.slap.ConnectionError as e:
        retries += 1
        if retries >= 60:
          raise
        logger.debug("Proxy still not started %s, retrying", e)
      else:
        break

    try:
      # register software profile
      for path in self.software_path_list:
        slap.registerSupply().supply(
            path,
            computer_guid=config['computer_id'])
    except Exception:
        logger.exception("SlapOSControler.initializeSlapOSControler")
        raise ValueError("Unable to registerSupply")
    # Reset all previously generated software if needed
    if reset_software:
      self._resetSoftware()
    else:
      createFolder(self.software_root)
    instance_root = self.instance_root
    # Delete any existing partition in order to not get its data (ex.
    # MySQL DB content) from previous runs. To support changes of partition
    # naming scheme (which already happened), do this at instance_root level.
    createFolder(instance_root, True)
    for i in range(MAX_PARTITIONS):
      # create partition and configure computer
      # XXX: at the moment all partitions do share same virtual interface address
      # this is not a problem as usually all services are on different ports
      partition_reference = '%s-%s' %(config['partition_reference'], i)
      partition_path = os.path.join(instance_root, partition_reference)
      if not(os.path.exists(partition_path)):
        os.mkdir(partition_path)
      os.chmod(partition_path, 0o750)
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

  def runSoftwareRelease(self, config, environment, **kw):
    logger.debug("SlapOSControler.runSoftwareRelease")
    # Set some flags to maximize CPU utilization
    # We usually have several testnode instances running on the same server, so
    # each testnode process should try to use the maximum amout of resources,
    # yet leaving some resources for other instances on the machine.
    # A typical scenario is we have all testnode re-compiling softwares at the
    # same time because of change in repository that would cause all test nodes
    # to recompile. That's why we try to do something a bit more clever than
    # "all testnodes uses all CPU available", because the total utilisation
    # will exceed the number of CPUs. Make allow fine tuning of its job server,
    # so we configure it to use all CPUs, unless the load is >= CPUs count.
    # numpy and rake does not expose such flexibility, so we just tell them to
    # use the number of CPUs this testnode instance was configured to use.
    cpu_count = str(os.sysconf("SC_NPROCESSORS_ONLN"))
    os.environ['MAKEFLAGS'] = '-j%s -l%s' % ( cpu_count, cpu_count)
    os.environ['NPY_NUM_BUILD_JOBS'] = config['node_quantity']
    os.environ['BUNDLE_JOBS'] = config['node_quantity']
    os.environ['PATH'] = environment['PATH']
    # a SR may fail for number of reasons (incl. network failures)
    # so be tolerant and run it a few times before giving up
    for _ in range(MAX_SR_RETRIES):
      status_dict = self.spawn(config['slapos_binary'],
                 'node', 'software', '--all', 
                 '--pidfile', os.path.join(self.software_root, 'slapos-node.pid'),
                 '--cfg', self.slapos_config, raise_error_if_fail=False,
                 log_prefix='slapgrid_sr', get_output=False)
      if status_dict['status_code'] == 0:
        break
    return status_dict

  def runComputerPartition(self, config, environment,
                           stdout=None, stderr=None, cluster_configuration=None,
                           max_quantity=MAX_PARTITIONS, **kw):
    logger.debug("SlapOSControler.runComputerPartition with cluster_config: %r",
             cluster_configuration)
    for path in self.software_path_list:
      try:
        self.slap.registerOpenOrder().request(path,
          partition_reference='testing partition %s' % \
            self.software_path_list.index(path),
          partition_parameter_kw=cluster_configuration)
      except Exception:
        logger.exception("SlapOSControler.runComputerPartition")
        raise ValueError("Unable to registerOpenOrder")

    # try to run for all partitions as one partition may in theory request another one 
    # this not always is required but curently no way to know how "tree" of partitions
    # may "expand"
    for _ in range(max_quantity):
      status_dict = self.spawn(config['slapos_binary'], 'node', 'instance', 
                 '--pidfile', os.path.join(self.instance_root, 'slapos-node.pid'),
                 '--cfg', self.slapos_config, raise_error_if_fail=False,
                 log_prefix='slapgrid_cp', get_output=False)
      logger.debug('slapgrid_cp status_dict : %r', status_dict)
      if not status_dict['status_code']:
        break
    else:
      # some hack to handle promise issues (should be only one of the two
      # codes, but depending on slapos versions, we have inconsistent status
      if status_dict['status_code'] in (1,2):
        status_dict['status_code'] = 0
    return status_dict