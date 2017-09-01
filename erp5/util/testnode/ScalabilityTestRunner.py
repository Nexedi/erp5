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
import SlapOSControler
import SlapOSMasterCommunicator
import json
import time
import shutil
import logging
import string
import random
import Utils
from ProcessManager import SubprocessError, ProcessManager, CancellationError
from subprocess import CalledProcessError
from Updater import Updater
from erp5.util import taskdistribution
# for dummy slapos answer
import signal

import slapos.slap



# max time to instance changing state: 2 hour
MAX_INSTANCE_TIME = 60*60*2
# max time to register instance to slapOSMaster: 5 minutes
MAX_CREATION_INSTANCE_TIME = 60*10
# max time for a test: 1 hour
MAX_TEST_CASE_TIME = 60*60

class ScalabilityTestRunner():
  def __init__(self, testnode):
    self.testnode =  testnode
    self.log = self.testnode.log
    
    self.slapos_controler = SlapOSControler.SlapOSControler(
                                  self.testnode.working_directory,
                                  self.testnode.config,
                                  self.log)
    # Create the slapos account configuration file and dir
    key = self.testnode.test_suite_portal.getSlaposAccountKey()
    certificate = self.testnode.test_suite_portal.getSlaposAccountCertificate()
    # Get Slapos Master Url
    self.slapos_url = ''
    try:
      self.slapos_url = self.testnode.test_suite_portal.getSlaposUrl()
      if not self.slapos_url:
        self.slapos_url = self.testnode.config['server_url']
    except:
      self.slapos_url = self.testnode.config['server_url']
    
    # Get Slapos Master url used for api rest (using hateoas)
    self.slapos_api_rest_url = self.testnode.test_suite_portal.getSlaposHateoasUrl()

    self.log("SlapOS Master url is: %s" %self.slapos_url)
    self.log("SlapOS Master hateoas url is: %s" %self.slapos_api_rest_url)
    
    self.key_path, self.cert_path, config_path = self.slapos_controler.createSlaposConfigurationFileAccount(
                                        key, certificate, self.slapos_url, self.testnode.config, self.slapos_api_rest_url)
    self.slapos_communicator = None
    # Dict containing used to store which SR is not yet correctly installed.
    # looks like: {'comp_id1':'SR_urlA', 'comp_id2':'SR_urlA',..}
    self.remaining_software_installation_dict = {}
    
    # Protection to prevent installation of softwares after checking
    self.authorize_supply = True
    self.authorize_request = False
    # Used to simulate SlapOS answer (used as a queue)
    self.last_slapos_answer = []
    self.last_slapos_answer_request = []
    
  def _prepareSlapOS(self, software_path, computer_guid, create_partition=0):
    # create_partition is kept for compatibility
    """
    A proxy to supply : Install a software on a specific node
    """
    self.log("SUPPLYING...")
    self.log("testnode, supply : %s %s", software_path, computer_guid)
    if self.authorize_supply :
      self.remaining_software_installation_dict[computer_guid] = software_path
      #self.slapos_controler.supply(software_path, computer_guid)

      self.slapos_communicator._supply("started")
      return {'status_code' : 0}                                          
    else:
      raise ValueError("Too late to supply now. ('self.authorize_supply' is False)")
      return {'status_code' : 1}     

  def _generateInstanceTitle(self, test_suite_title):
    """
    Generate an instance title using various parameter
    TODO : add some verification (to don't use unexisting variables)
    """
    instance_title = "Scalability-"
    instance_title += "("+test_suite_title+")-"
    instance_title += str(self.involved_nodes_computer_guid).replace("'","")
    #instance_title += "-"+str(datetime.datetime.now().isoformat())+"-"
    #instance_title += "timestamp="+str(time.time())
    return instance_title

  def _generateInstanceXML(self, software_configuration,
                      test_result, test_suite):
    """
    Generate a complete scalability instance XML configuration
    """
    config_cluster = software_configuration.copy()
    #config = {'cluster':config_cluster}
    # ROQUE: Avoiding to use key 'cluster'. Directly pass the content 
    config = config_cluster   
    config.update({'scalability-launcher-computer-guid':self.launcher_nodes_computer_guid[0]})
    config.update({'scalability-launcher-title':'MyTestNodeTitle'})
    config.update({'test-result-path':test_result.test_result_path})
    config.update({'test-suite-revision':test_result.revision})
    config.update({'test-suite':test_suite})
    config.update({'test-suite-master-url':self.testnode.config['test_suite_master_url']})
    return config
  
  def _createInstance(self, software_path, software_configuration, instance_title,
                      test_result, test_suite):
    """
    Create scalability instance
    """
    if self.authorize_request:
      config = self._generateInstanceXML(software_configuration,
                                    test_result, test_suite)
      self.log("testnode, request : %s", instance_title)
      config = json.dumps(config)
      #request_kw = {"_" : config}
      request = {"_" : config}
      request_kw = {"partition_parameter_kw": request } 
      #self.log("config from software_configuration, test_result & test_suite: " + str(config))
      #self.log("request_kw: " + str(request_kw))
      #self.log("Computer : " + str(self.launcher_nodes_computer_guid[0]))
      #self.slapos_controler.request(instance_title, software_path,
      #                       "test", {"_" : config},
      #                       self.launcher_nodes_computer_guid[0])
      self.slapos_communicator.setName(instance_title)
      self.slapos_communicator.setRequestParameters(request_kw)
      comp_partition = self.slapos_communicator._request("started")
      #self.log("Computer partition certificate:")
      #self.log(str(comp_partition.getCertificate()))
      #self.slapos_communicator.forceSetState('started')
      self.authorize_request = False
      return {'status_code' : 0}                                          
    else:
      raise ValueError("Softwares release not ready yet to launch instan\
ces or already launched.")
      return {'status_code' : 1}  
      
  def prepareSlapOSForTestNode(self, test_node_slapos=None):
    """
    We will build slapos software needed by the testnode itself,
    """
    if self.testnode.test_suite_portal.isMasterTestnode(
                           self.testnode.config['test_node_title']):
      pass
    return {'status_code' : 0} 

  # Dummy slapos answering
  def _getSignal(self, signal, frame):
    self.log("Dummy SlapOS Master answer received.")
    self.last_slapos_answer.append(True)
  def _prepareDummySlapOSAnswer(self):
    self.log("Dummy slapOS answer enabled, send signal to %s (kill -10 %s) to simu\
late a SlapOS (positive) answer." %(str(os.getpid()),str(os.getpid()),))
    signal.signal(signal.SIGUSR1, self._getSignal)
  def _comeBackFromDummySlapOS(self):
    self.log("Dummy slapOS answer disabled, please don't send more signals.")
    # use SIG_USR (kill)
    signal.signal(signal.SIGUSR1, signal.SIG_DFL)
  def simulateSlapOSAnswer(self):
    if len(self.last_slapos_answer)==0:
      return False
    else:
      return self.last_slapos_answer.pop()
  # /Dummy slapos answering
    
  def isSoftwareReleaseReady(self, software_url, computer_guid):
    """
    Return true if the specified software on the specified node is installed.
    This method should communicates with SlapOS Master.
    """
    # TODO : implement -> communication with SlapOS master
    # this simulate a SlapOS answer
    #return self.simulateSlapOSAnswer()
    self.log("Current software state: " + str(self.slapos_communicator._getSoftwareState()))
    return self.slapos_communicator._getSoftwareState() == SlapOSMasterCommunicator.SOFTWARE_STATE_INSTALLED
  
  def remainSoftwareToInstall(self):
    """
    Return True if it remains softwares to install, otherwise return False
    """
    # Remove from grid installed software entries
    for computer_guid, software_path in self.remaining_software_installation_dict.items():
      if self.isSoftwareReleaseReady(software_path, computer_guid):
        del self.remaining_software_installation_dict[computer_guid]
    # Not empty grid means that all softwares are not installed
    return len(self.remaining_software_installation_dict) > 0

  def _updateInstanceXML(self, software_configuration, instance_title,
                      test_result, test_suite):
    """
    Just a proxy to SlapOSControler.updateInstanceXML.
    """
    config = self._generateInstanceXML(software_configuration,
                                  test_result, test_suite)
    config = json.dumps(config)
    self.log("testnode, updateInstanceXML : %s", instance_title)
    #self.slapos_controler.updateInstanceXML(instance_title, {"_" : config})
    request = {"_" : config}
    request_kw = {"partition_parameter_kw": request }
    self.slapos_communicator.setRequestParameters(request_kw)
    self.slapos_communicator._request("started")
    return {'status_code' : 0} 

  def _waitInstance(self, instance_title, state, max_time=MAX_INSTANCE_TIME):
    """
    Wait for 'max_time' an instance specific state
    """
    self.log("Wait for instance state: %s" %state)
    start_time = time.time()
    #while (not self.slapos_communicator.isHostingSubscriptionReady(instance_title, state)
    while (not self.slapos_communicator._getInstanceState() == state
         and (max_time > (time.time()-start_time))):
      self.log("Instance(s) not in %s state yet." % state)
      time.sleep(15)
    if (time.time()-start_time) > max_time:
      error_message = "Instance '%s' not '%s' after %s seconds" %(instance_title, state, str(time.time()-start_time))
      self.log(error_message)
      self.log("Do you use instance state propagation in your project?")
      self.log("Instance '%s' will be stopped and test avorted." %instance_title)
      # What if we wanted to stop ?
      #self.slapos_controler.stopInstance(instance_title)
      #self.slapos_communicator._request('stopped')
      # XXX: _waitInstance call here ? recursive call ?
      # XXX: sleep 60 seconds.
      time.sleep(60) 
      raise ValueError(error_message)
    self.log("Instance correctly '%s' after %s seconds." %(state, str(time.time()-start_time)))

  def _waitInstanceCreation(self, instance_title, hateoas,  max_time=MAX_CREATION_INSTANCE_TIME):
    """
    Wait for 'max_time' the instance creation
    """
    self.log("Instance title: " + str(instance_title))
    self.log("Waiting for instance creation...")
    start_time = time.time()
    #self.log("List of Hosting subscriptions : ")
    #self.log(str(hateoas.getHostingSubscriptionDict()))
    #while ( not self.slapos_communicator.isRegisteredHostingSubscription(instance_title) \
    self.log("Current instances: ")
    self.log(str(hateoas.getHostingSubscriptionDict()))
    self.printCommunicatorInfo("COMP-2732")
    while (not instance_title in hateoas.getHostingSubscriptionDict() \
         and (max_time > (time.time()-start_time)) ):
      self.log("Instance not ready yet. Sleeping 5 sec.")
      self.printCommunicatorInfo("COMP-2732")
      time.sleep(5)
    if (time.time()-start_time) > max_time:
      raise ValueError("Instance '%s' not found after %s seconds" %(instance_title, max_time))
    self.log("Instance found on slapOSMaster")

  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Install testsuite softwares
    """
    self.log('Preparing SlapOS for Test Suite...')
    # Define how many time this method can take
    max_time = 3600*10*1.0 # 10 hours
    interval_time = 60
    start_time = time.time()
    #self.log("CERT: " + str(self.cert_path))
    #self.log("KEY: " + str(self.key_path))
    #self.log("API URL: " + str(self.slapos_api_rest_url))
    #self.log("MASTER URL: " + str(self.slapos_url))

    ### NEW ! Creating Slapos master communicator ###
    slap = slapos.slap.slap()
    retry = 0
    while True:
      if retry > 100:
         break
      # wait until _hateoas_navigator is loaded.
      slap.initializeConnection(
        self.slapos_url, self.key_path, self.cert_path, timeout=120, slapgrid_rest_uri=self.slapos_api_rest_url)

      if getattr(slap, '_hateoas_navigator', None) is None:
         retry += 1
         self.log("Fail to load _hateoas_navigator waiting a bit and retry.")
         time.sleep(30)
      else:
         break

    if getattr(slap, '_hateoas_navigator', None) is None:
      raise ValueError("Fail to load _hateoas_navigator")

    hateoas = getattr(slap, '_hateoas_navigator', None)
    #self.log("_hateoas_navigator object ")
    #self.log(".getHostingSubscriptionDict()")
    #self.log(hateoas.getHostingSubscriptionDict())
    #self.log("_hateoasGetInformation()")
    #self.log(hateoas._hateoasGetInformation("nxdcloud-onlinenet-scalabilitynode-001-ERP5SCALABILITY"))
    #self.log("getHostingSubscriptionRootSoftwareInstanceInformation(node)")
    #self.log(hateoas.getHostingSubscriptionRootSoftwareInstanceInformation("nxdcloud-onlinenet-scalabilitynode-001-ERP5SCALABILITY"))
    #self.log(".getRelatedInstanceInformation(node)")
    #self.log(hateoas.getRelatedInstanceInformation("nxdcloud-onlinenet-scalabilitynode-001-ERP5SCALABILITY"))

    supply = slap.registerSupply()
    order = slap.registerOpenOrder()

    ### //NEW ! ###

    # Only master testnode must order software installation
    if self.testnode.test_suite_portal.isMasterTestnode(
            self.testnode.config['test_node_title']):
      # Get from ERP5 Master the configuration of the cluster for the test
      test_configuration = Utils.deunicodeData(
          json.loads(self.testnode.test_suite_portal.generateConfiguration(
                      node_test_suite.test_suite_title)
                    )
        )
      self.involved_nodes_computer_guid = test_configuration['involved_nodes_computer_guid']
      self.launchable = test_configuration['launchable']
      self.error_message = test_configuration['error_message']
      self.randomized_path = test_configuration['randomized_path']
      # Avoid the test if it is not launchable
      if not self.launchable:
        self.log("Test suite %s is not actually launchable with \
  the current cluster configuration." %(node_test_suite.test_suite_title,))
        self.log("ERP5 Master indicates : %s" %(self.error_message,))
        # error : wich code to return ?
        return {'status_code' : 1}

      involved_nodes_computer_guid = test_configuration['involved_nodes_computer_guid']
      configuration_list = test_configuration['configuration_list']
      node_test_suite.edit(configuration_list=configuration_list)
      self.launcher_nodes_computer_guid = test_configuration['launcher_nodes_computer_guid']
      
      # Create an obfuscated link to the testsuite directory
      self.log("### Creating an obfuscated link to the testsuite directory")
      path_to_suite = os.path.join(
                      self.testnode.config['working_directory'],
                      node_test_suite.reference)
      self.log("Path to suite: " + path_to_suite)
      self.obfuscated_link_path = os.path.join(
                      self.testnode.config['software_directory'],
                      self.randomized_path)
      self.log("Obfuscated path: " + self.obfuscated_link_path)
      if ( not os.path.lexists(self.obfuscated_link_path) and
           not os.path.exists(self.obfuscated_link_path) ) :
        try :
          os.symlink(path_to_suite, self.obfuscated_link_path)
          self.log("testnode, Symbolic link (%s->%s) created."
                   %(self.obfuscated_link_path, path_to_suite))
        except :
          self.log("testnode, Unable to create symbolic link to the testsuite.")
          raise ValueError("testnode, Unable to create symbolic link to the testsuite.")
      self.log("Sym link : %s %s" %(path_to_suite, self.obfuscated_link_path))
      
      # Construct the ipv6 obfuscated url of the software profile reachable from outside
      self.log("Constructing the ipv6 obfuscated url of the software profile reachable from outside")
      self.reachable_address = os.path.join(
        "https://","["+self.testnode.config['httpd_ip']+"]"+":"+self.testnode.config['httpd_software_access_port'],
        self.randomized_path)
      self.reachable_profile = os.path.join(self.reachable_address, "software.cfg")
      # ROQUE: hardcoded software url until installation bug is solved
      self.reachable_address = "https://lab.nexedi.com/rporchetto/telecom/tree/master"
      self.reachable_profile = "https://lab.nexedi.com/rporchetto/telecom/raw/master/software_release/software.cfg"
      self.log("Reachable address: " + self.reachable_address)
      self.log("Reachable profile: " + self.reachable_profile)

      # Write the reachable address in the software.cfg file,
      # by replacing <obfuscated_url> occurences by the current reachable address.
      software_file = open(node_test_suite.custom_profile_path, "r")
      self.log("Writing obfuscated url in software.cfg file: " + node_test_suite.custom_profile_path)
      file_content = software_file.readlines()
      new_file_content = []
      for line in file_content:
        new_file_content.append(line.replace('<obfuscated_url>', self.reachable_address))
      software_file.close()
      os.remove(node_test_suite.custom_profile_path)
      software_file = open(node_test_suite.custom_profile_path, "w")
      for line in new_file_content:
        software_file.write(line)
      software_file.close()
      self.log("Software reachable profile path is : %s "
                              %(self.reachable_profile,))

      # Ask for SR installation
      for computer_guid in self.involved_nodes_computer_guid:
        self.slapos_communicator = SlapOSMasterCommunicator.SoftwareReleaseTester("NAME", self.log, slap, order, supply, self.reachable_profile, computer_guid=computer_guid)
        # ROQUE: _prepareSlapOS commented because software installation fails.
        self._prepareSlapOS(self.reachable_profile, computer_guid) 
      # From the line below we would not supply any more softwares
      self.authorize_supply = False
      # TODO : remove the line below wich simulate an answer from slapos master
      self._prepareDummySlapOSAnswer()
      # Waiting until all softwares are installed
      while ( self.remainSoftwareToInstall() 
         and (max_time > (time.time()-start_time))):
        self.log("Master testnode is waiting\
 for the end of all software installation (for %ss) PID=%s.",
          str(int(time.time()-start_time)), str(os.getpid()))
        self.printCommunicatorInfo("COMP-2732")
        time.sleep(interval_time)
      # TODO : remove the line below wich simulate an answer from slapos master
      self._comeBackFromDummySlapOS()
      if self.remainSoftwareToInstall() :
        # All softwares are not installed, however maxtime is elapsed, that's a failure.
        return {'status_code' : 1}
      self.authorize_request = True
      self.log("Softwares installed")
      # Launch instance
      self.instance_title = self._generateInstanceTitle(node_test_suite.test_suite_title)
      try:
        self._createInstance(self.reachable_profile, configuration_list[0],
                             self.instance_title, node_test_suite.test_result, node_test_suite.test_suite)
        self.log("Scalability instance requested.")
      except:
        self.log("Unable to launch instance")
        raise ValueError("Unable to launch instance")
      self._waitInstanceCreation(self.instance_title, hateoas)

      return {'status_code' : 0}
    return {'status_code' : 1}


  def runTestSuite(self, node_test_suite, portal_url):
    if not self.launchable:
      self.log("Current test_suite is not actually launchable.")
      return {'status_code' : 1} # Unable to continue due to not realizable configuration
    configuration_list = node_test_suite.configuration_list
    #self.log("CONFIGURATION LIST:")
    #self.log(str(configuration_list))
    test_list = range(0, len(configuration_list))
    # create test_result
    self.log("Creating Test Result...")
    test_result_proxy = self.testnode.portal.createTestResult(
      node_test_suite.revision, test_list,
      self.testnode.config['test_node_title'],
      True, node_test_suite.test_suite_title,
      node_test_suite.project_title)
    self.log("Test Result created.") 
    count = 0
    error_message = None

    self.log("[DEBUG] WAITING INSTANCE STATE STARTED...")
    self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STARTED)

    # Each cluster configuration are tested
    #self.log("[DEBUG] Number of configurations: " + str(len(configuration_list)))
    #self.log("[DEBUG] FOR EACH CONFIGURATION: ")
    for configuration in configuration_list:
      #self.log(str(configuration))

      # First configuration doesn't need XML configuration update.
      if count > 0:
        self.log("[DEBUG] COUNT > 0 : updating XML configuration...")
        # Stop instance
        #self.slapos_controler.stopInstance(self.instance_title)
        self.slapos_communicator._request('stopped')
        self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STOPPED)
        # Update instance XML configuration 
        self._updateInstanceXML(configuration, self.instance_title,
                      node_test_suite.test_result, node_test_suite.test_suite)
        self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STARTED)
        # Start instance
        #self.slapos_controler.startInstance(self.instance_title)
        self.slapos_communicator._request('started')
        
      '''
      # XXX: Dirty hack used to force haproxy to restart in time
      # with all zope informations.
      self.log("[DEBUG] HACK- waiting instance started")
      self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STARTED)
      #self.slapos_controler.stopInstance(self.instance_title)
      self.log("[DEBUG] HACK- stopping instance")
      self.slapos_communicator._request('stopped')
      self.log("[DEBUG] HACK- waiting instance stopped")
      self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STOPPED)
      self.log("[DEBUG] HACK- starting instance")
      self.slapos_communicator._request('started')
      #self.slapos_controler.startInstance(self.instance_title)
      ##########################################################
      '''        

      self.log("[DEBUG] waiting instance started")
      self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STARTED)
      self.log("[DEBUG] INSTANCE CORRECTLY STARTED")
      
      if True:
        self.log("FORCE QUITTING BEFORE RUN THE TESTS.")
        return {'status_code' : 1 , 'error_message' : 'FORCE QUITTING FOR DEBUG'} 

      # Start only the current test
      exclude_list=[x for x in test_list if x!=test_list[count]]
      count += 1
      test_result_line_proxy = test_result_proxy.start(exclude_list)

      # 
      if test_result_line_proxy == None :
        error_message = "Test case already tested."
        break

      self.log("Test for count : %d is in a running state." %count)

      # Wait for test case ending
      test_case_start_time = time.time()
      while test_result_line_proxy.isTestCaseAlive() and \
            test_result_proxy.isAlive() and \
            time.time() - test_case_start_time < MAX_TEST_CASE_TIME:
        time.sleep(15)

      # Max time limit reach for current test case: failure.
      if test_result_line_proxy.isTestCaseAlive():
        error_message = "Test case during for %s seconds, too long. (max: %s seconds). Test failure." \
                            %(str(time.time() - test_case_start_time), MAX_TEST_CASE_TIME)
        break

      # Test cancelled, finished or in an undeterminate state.
      if not test_result_proxy.isAlive():
        # Test finished
        if count == len(configuration_list):
          break
        # Cancelled or in an undeterminate state.
        error_message = "Test cancelled or undeterminate state."
        break

    # Stop current instance
    #self.slapos_controler.stopInstance(self.instance_title)
    self.slapos_communicator._request('stopped')
    self._waitInstance(self.instance_title, SlapOSMasterCommunicator.INSTANCE_STATE_STOPPED)

    # Delete old instances
    self._cleanUpOldInstance()

    # If error appears then that's a test failure.    
    if error_message:
      test_result_line_proxy.stop(error_count=1, failure_count=1,
                                  stdout=error_message, stderr=error_message)
      test_result_proxy.reportFailure(stdout=error_message)
      self.log("Test Failed.")
      return {'status_code' : 1, 'error_message': error_message} 
    # Test is finished.
    self.log("Test finished.")
    return {'status_code' : 0}

  def _cleanUpOldInstance(self):
    self.log("_cleanUpOldInstance")

    # Get title and link list of all instances
    instance_dict = self.slapos_communicator.getHostingSubscriptionDict()
    instance_to_delete_list = []
    outdated_date = datetime.datetime.fromtimestamp(time.time()) - datetime.timedelta(days=2)

    # Select instances to delete
    for title,link in instance_dict.items():
      # Instances created by testnode contains "Scalability-" and
      # "timestamp=" in the title.
      if "Scalability-" in title and "timestamp=" in title:
        # Get timestamp of the instance creation date
        foo, timestamp = title.split("timestamp=")
        creation_date = datetime.datetime.fromtimestamp(float(timestamp))
        # Test if instance is older than the limit
        if creation_date < outdated_date:
          instance_to_delete_list.append((title,link))
    
    for title,link in instance_to_delete_list:
      # Get instance information
      instance_information_dict = self.slapos_communicator.getHostingSubscriptionInformationDict(title)
      # Delete instance
      if instance_information_dict:
        if instance_information_dict['status'] != 'destroyed':
          self.slapos_controler.request(
              instance_information_dict['title'],
              instance_information_dict['software_url'],
              software_type=instance_information_dict['software_type'],
              computer_guid=instance_information_dict['computer_guid'],
              state='destroyed'
          )
          self.log("Instance '%s' deleted." %instance_information_dict['title'])

  def _cleanUpNodesInformation(self):
    self.involved_nodes_computer_guid = []
    self.launcher_nodes_computer_guid = []
    self.remaining_software_installation_dict = {}
    self.authorize_supply = True
    self.authorize_request = False

  def getRelativePathUsage(self):
    """
    Used by the method testnode.constructProfile() to know
    if the software.cfg have to use relative path or not.
    """
    return True
 
  def printCommunicatorInfo(self, computer_id, instance_url=None):
    self.log("################ PRINTING SLAPOS MASTER COMMUNICATOR INFO ################")
    #computer = self.slapos_communicator._hateoas_getComputer("COMP-2732")
    computer = self.slapos_communicator._hateoas_getComputer(computer_id)
    if computer is not None:
      #self.log("COMPUTER: " + str(computer))
      software_installation_list = self.slapos_communicator.getSoftwareInstallationList()
      self.log("software_installation_list: ")
      self.log(str(software_installation_list))
      getSoftwareInstallationNews = self.slapos_communicator.getSoftwareInstallationNews()
      self.log("Software installation news: ")
      #self.log(str(getSoftwareInstallationNews))
      #getInstanceUrlList = self.slapos_communicator.getInstanceUrlList()
      #self.log("getInstanceUrlList")
      #self.log(str(getInstanceUrlList))
      # ROQUE: for debugging purposes

      if instance_url is not None:
        #instance_url = 'https://api.vifib.com/software_instance_module/20170822-1568166F/ERP5Document_getHateoas'
        self.log("getNewsFromInstance(url)")
        self.log(str(self.slapos_communicator.getNewsFromInstance(instance_url)))
        self.log("getInformationFromInstance(url)")
        self.log(str(self.slapos_communicator.getInformationFromInstance(instance_url)))

      # ROQUE: get info contains the software release url
      getInfo = self.slapos_communicator.getInfo()
      self.log("getInfo: ")
      self.log(str(getInfo))

      # Always return "No message"
      #getFormatedLastMessage = self.slapos_communicator.getFormatedLastMessage()
      #self.log("getFormatedLastMessage: ")
      #self.log(str(getFormatedLastMessage))

      getSoftwareState = self.slapos_communicator._getSoftwareState()
      self.log("Software state: " + str(getSoftwareState))

      getInstanceState = self.slapos_communicator._getInstanceState()
      self.log("Instance state: " + str(getInstanceState))
    self.log("##########################################################################")


