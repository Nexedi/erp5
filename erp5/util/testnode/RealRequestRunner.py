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
import datetime
import os
import subprocess
import sys
import time
import glob
from . import SlapOSControler, SlapOSMasterCommunicator
import json
import time
import shutil
import logging
import string
import random
from six.moves.urllib.parse import urlparse
import base64
from six.moves import http_client as httplib
from .Utils import createFolder, deunicodeData, dealShebang
from slapos.grid.utils import md5digest
import requests
import slapos.slap
from .ProcessManager import SubprocessError, ProcessManager, CancellationError, format_command
from subprocess import CalledProcessError
from .Updater import Updater
from erp5.util import taskdistribution
from erp5.util.benchmark.thread import TestThread
# for dummy slapos answer
import signal
from . import logger

from six.moves import range

# max time to generate frontend instance: 1.5 hour
MAX_FRONTEND_TIME = 60*90
# max time to register instance to slapOSMaster: 5 minutes
MAX_CREATION_INSTANCE_TIME = 60*10
# max time for a test: 20 minutes
MAX_TEST_CASE_TIME = 60*20
# max time to prepare SlapOS for testsuite (software installation, instances requests, etc.)
MAX_PREPARE_TEST_SUITE = 3600*10*1.0 # 10 hours
# max time for a test line creation: 5 minutes
MAX_CREATION_TEST_LINE = 60*10
# max time for bootstrapping an instance site
MAX_BOOTSRAPPING_TIME = 60*30
# max time to get a connection
MAX_CONNECTION_TIME = 60*5
# time to check site bootstrap
CHECK_BOOSTRAPPING_TIME = 60*2

# runner names
PERFORMANCE_RUNNER_SCRIPT = "performance_tester_erp5"
REQUEST_URL_SCRIPT = "requestUrl"
SCALABILITY_TEST = "scalability_test"
TEST_SUITE_INIT = "__init__.py"

# access SR by password
TESTNODE_USER = "testnode"
HTACCESS = "/.htaccess"
HTPASSWD = "/.htpasswd"
PASSWORD_FILE = "/sr_pass"
PASSWORD_LENGTH = 10
HOSTFILE = "/hosts"
SR_DICT = "frontend_software_dict"
INSTANCE_DICT = "instances_dict"

class RealRequestRunner():
  def __init__(self, testnode):
    self.testnode =  testnode
    self.slapos_controler = SlapOSControler.SlapOSControler(
                                  self.testnode.working_directory,
                                  self.testnode.config)
    # Create the slapos account configuration file and dir
    key = self.testnode.taskdistribution.getSlaposAccountKey()
    certificate = self.testnode.taskdistribution.getSlaposAccountCertificate()

    # Get Slapos Master Url
    self.slapos_url = ''
    try:
      self.slapos_url = self.testnode.taskdistribution.getSlaposUrl()
      if not self.slapos_url:
        self.slapos_url = self.testnode.config['server_url']
    except Exception:
      self.slapos_url = self.testnode.config['server_url']
    
    # Get Slapos Master url used for api rest (using hateoas)
    self.slapos_api_rest_url = self.testnode.taskdistribution.getSlaposHateoasUrl()

    logger.info("SlapOS Master url is: %s", self.slapos_url)
    logger.info("SlapOS Master hateoas url is: %s", self.slapos_api_rest_url)
    
    self.key_path, self.cert_path, config_path = self.slapos_controler.createSlaposConfigurationFileAccount(
                                        key, certificate, self.slapos_url, self.testnode.config)
    self.slapos_communicator_list = []
    # Dict containing all info about SlapOS instances requested for the test
    # looks like
    # {
    #   instance1_title: {
    #     
    # 
    # }
    # }
    self.instances_parameters_dict = {}

  def _generateInstanceTitle(self, service_title):
    """
    Generate an instance title using various parameter
    TODO : add some verification (to don't use unexisting variables)
    """
    instance_title = "E2E.Amarisoft-"
    instance_title += "("+service_title+")-"
    instance_title += str(datetime.datetime.now().isoformat())+"-"
    instance_title += "timestamp="+str(time.time())
    return instance_title

  def getDictionaryFromFile(self, dict_file):
    dictionary = {}
    if os.path.isfile(dict_file):
      with open(dict_file, 'r') as file:
        dictionary = json.loads(file.read())
    return dictionary

  def updateDictionaryFile(self, dict_file, dictionary):
    with open(dict_file, 'w') as file:
      file.write(json.dumps(dictionary))                                     

  def _prepareSlapOS(self, working_directory, slapos_instance,
          create_partition=1, software_path_list=None, use_local_shared_part=False, **kw):
    """
    Launch slapos to build software and partitions
    """
    slapproxy_log = os.path.join(self.testnode.config['log_directory'],
                                  'slapproxy.log')
    logger.debug('Configured slapproxy log to %r', slapproxy_log)
    reset_software = slapos_instance.retry_software_count > 10
    if reset_software:
      slapos_instance.retry_software_count = 0
    logger.info('testnode, retry_software_count: %r',
             slapos_instance.retry_software_count)

    self.slapos_controler.initializeSlapOSControler(slapproxy_log=slapproxy_log,
       process_manager=self.testnode.process_manager, reset_software=reset_software,
       software_path_list=software_path_list)
    self.testnode.process_manager.supervisord_pid_file = os.path.join(\
         self.slapos_controler.instance_root, 'var', 'run', 'supervisord.pid')
    method_list= ["runSoftwareRelease"]
    if create_partition:
      method_list.append("runComputerPartition")
    for method_name in method_list:
      slapos_method = getattr(self.slapos_controler, method_name)
      logger.debug("Before status_dict = slapos_method(...)")
      status_dict = slapos_method(self.testnode.config,
                                  environment=self.testnode.config['environment'],
                                  **kw)
      logger.info(status_dict)
      logger.debug("After status_dict = slapos_method(...)")
      if status_dict['status_code'] != 0:
         slapos_instance.retry = True
         slapos_instance.retry_software_count += 1
         raise SubprocessError(status_dict)
      else:
         slapos_instance.retry_software_count = 0
    return status_dict

  def prepareSlapOSForTestNode(self, test_node_slapos):
    """
    We will build slapos software needed by the testnode itself,
    like the building of selenium-runner by default
    """
    return {'status_code' : 0}

  def _initializeSlapOSConnection(self):
    """
    Initialize communication with slapos 
    """
    slap = slapos.slap.slap()
    retry = 0
    while True:
      # wait until _hateoas_navigator is loaded.
      if retry > 100:
         break
      slap.initializeConnection(self.slapos_url, 
                                self.key_path, 
                                self.cert_path, 
                                timeout=120, 
                                slapgrid_rest_uri=self.slapos_api_rest_url)
      if getattr(slap, '_hateoas_navigator', None) is None:
         retry += 1
         logger.info("Fail to load _hateoas_navigator waiting a bit and retry.")
         time.sleep(30)
      else:
         break

    if getattr(slap, '_hateoas_navigator', None) is None:
      raise ValueError("Fail to load _hateoas_navigator")

    supply = slap.registerSupply()
    order = slap.registerOpenOrder()
    return slap, supply, order

  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Install testsuite softwares
    """
    logger.debug('Preparing SlapOS for Test Suite...')
    logger.info(node_test_suite)
    result = self._prepareSlapOS(node_test_suite.working_directory,
              node_test_suite,
              software_path_list=[node_test_suite.custom_profile_path],
              cluster_configuration={'_': json.dumps(node_test_suite.cluster_configuration)},
              use_local_shared_part=True)
    if result['status_code'] != 0:
      return result
    slappart_directory = self.testnode.config['srv_directory'].rsplit("srv", 1)[0]
    instance_dict_file = slappart_directory + "var/" + INSTANCE_DICT
    test_suite = node_test_suite.test_suite_title
    # Initialize communication with slapos
    slap, supply, order = self._initializeSlapOSConnection()

    # Destroy previous instances
    instance_dict = self.getDictionaryFromFile(instance_dict_file)
    if test_suite in instance_dict:
      instance_list = instance_dict[test_suite]
      for instance_title,instance_is_shared in list(instance_list):
        logger.info("Destroying previous instance %s", instance_title)
        order.request(
          software_release="dummy_SR_just_to_destroy", # XXX empty string is not supported...
          partition_reference=instance_title,
          shared=instance_is_shared,
          state="destroyed")
        del instance_list[0]
        instance_dict[test_suite] = instance_list
        self.updateDictionaryFile(instance_dict_file, instance_dict)

    # Get from ERP5 Master the configuration of the cluster for the test
    service_list = deunicodeData(
        json.loads(self.testnode.taskdistribution.getServiceList(
                   node_test_suite.test_suite_title)))
    logger.info('List of service is %s', service_list)
    instance_list = [] # instance_list should already be an empty list (but it may not have been initialised if testsuite seen for the first time)
    for service in service_list.values():
      logger.info(service)
      instance_title = self._generateInstanceTitle(service['title'])
      software_release = service['url']
      logger.info("Will request instance %s of %s (software_type %s)", instance_title, software_release, service['software_type'])
      s = SlapOSMasterCommunicator.SlapOSTester(
                                           instance_title,
                                           slap,
                                           order,
                                           supply,
                                           software_release)
      self.slapos_communicator_list.append(s)
      partition_parameter_kw = json.loads(service['partition_parameter_kw'])
      if len(partition_parameter_kw) == 1 and '_' in partition_parameter_kw:
        partition_parameter_kw['_'] = json.dumps(partition_parameter_kw ['_'])
      request_kw = {
        'partition_parameter_kw' : partition_parameter_kw,
        'filter_kw' : json.loads(service['filter_kw'])
        }
      s.requestInstanceStart(
        request_kw=request_kw,
        shared=service['shared'],
        software_type=service['software_type']
      )
      instance_list.append((instance_title,service['shared']))
      instance_dict[test_suite] = instance_list
      self.updateDictionaryFile(instance_dict_file, instance_dict)

    logger.debug("Instances requested.")
    return {'status_code' : 0}

  def runTestSuite(self, node_test_suite, portal_url):
    # Wait all instances are started
    for s in self.slapos_communicator_list:
      try:
        s.waitInstanceStarted()
        self.instances_parameters_dict[s.name] = s.getInstanceParameterDict()
      except Exception as e:
        error_message = "Error starting instance " + s.name + ": " + str(e)
        return {'status_code' : 1, 'error_message': error_message }
    
    instances_parameters_file = os.path.join(self.testnode.config['srv_directory'], "instances.json")
    with open(instances_parameters_file, 'w') as file:
      file.write(json.dumps(self.instances_parameters_dict))     
    logger.debug("ALL INSTANCES CORRECTLY STARTED")



    config = self.testnode.config
    run_test_suite_path_list = glob.glob(
        self.slapos_controler.instance_root + "/*/bin/runTestSuite")
    try:
      run_test_suite_path = min(run_test_suite_path_list)
    except ValueError:
      raise ValueError('No runTestSuite provided in installed partitions.')
    # Deal with Shebang size limitation
    invocation_list = dealShebang(run_test_suite_path)
    invocation_list += (run_test_suite_path,
      '--master_url', portal_url,
      '--revision', node_test_suite.revision,
      '--test_node_title', config['test_node_title'],
      '--test_suite', node_test_suite.test_suite,
      '--test_suite_title', node_test_suite.test_suite_title)
    soft = config['slapos_directory'] + '/soft/'
    software_list = [soft + md5digest(x) for x in config['software_list']]
    PATH = os.getenv('PATH', '')
    PATH = ':'.join(x + '/bin' for x in software_list) + (PATH and ':' + PATH)
    SLAPOS_TEST_SHARED_PART_LIST = os.pathsep.join(
        self.slapos_controler.shared_part_list)
    SLAPOS_TEST_LOG_DIRECTORY = node_test_suite.log_folder_path
    supported_parameter_set = set(self.testnode.process_manager
      .getSupportedParameterList(run_test_suite_path))
    def path(name, compat): # BBB
        path, = filter(os.path.exists, (base + relative
          for relative in ('/bin/' + name, '/parts/' + compat)
          for base in software_list))
        return path
    for option, value in (
        ('--firefox_bin', lambda: path('firefox', 'firefox/firefox-slapos')),
        ('--frontend_url', lambda: config['frontend_url']),
        ('--node_quantity', lambda: config['node_quantity']),
        ('--xvfb_bin', lambda: path('xvfb', 'xserver/bin/Xvfb')),
        ('--project_title', lambda: node_test_suite.project_title),
        ('--shared_part_list', lambda: SLAPOS_TEST_SHARED_PART_LIST),
        ('--log_directory', lambda: SLAPOS_TEST_LOG_DIRECTORY),
        ):
      if option in supported_parameter_set:
        invocation_list += option, value()

    # TODO : include testnode correction ( b111682f14890bf )
    if hasattr(node_test_suite,'additional_bt5_repository_id'):
      additional_bt5_path = os.path.join(
              node_test_suite.working_directory,
              node_test_suite.additional_bt5_repository_id)
      invocation_list.extend(["--bt5_path", additional_bt5_path])
    # From this point, test runner becomes responsible for updating test
    # result. We only do cleanup if the test runner itself is not able
    # to run.
    createFolder(node_test_suite.test_suite_directory, clean=True)

    # Log the actual command with root logger
    root_logger = logging.getLogger()
    root_logger.info(
        "Running test suite with: %s",
        format_command(*invocation_list, PATH=PATH))

    def hide_distributor_url(s):
      # type: (bytes) -> bytes
      return s.replace(portal_url.encode('utf-8'), b'$DISTRIBUTOR_URL')

    self.testnode.process_manager.spawn(*invocation_list, PATH=PATH,
                          SLAPOS_TEST_SHARED_PART_LIST=SLAPOS_TEST_SHARED_PART_LIST,
                          SLAPOS_TEST_LOG_DIRECTORY=SLAPOS_TEST_LOG_DIRECTORY,
                          SLAPOS_INSTANCES_PARAMETERS_FILE=instances_parameters_file,
                          cwd=node_test_suite.test_suite_directory,
                          log_prefix='runTestSuite',
                          output_replacers=(hide_distributor_url,),
                          get_output=False)
    return {'status_code' : 0}
    
  def getRelativePathUsage(self):
    """
    Used by the method testnode.constructProfile() to know
    if the software.cfg have to use relative path or not.
    """
    return False
