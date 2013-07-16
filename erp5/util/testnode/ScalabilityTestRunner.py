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
from datetime import datetime,timedelta
import os
import subprocess
import sys
import time
import glob
import SlapOSControler
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
    self.slapos_controler.createSlaposConfigurationFileAccount(key,certificate,
                                    self.testnode.config)
                              
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
    self.log("testnode, supply : %s %s", software_path, computer_guid)
    if self.authorize_supply :
      self.remaining_software_installation_dict[computer_guid] = software_path
      self.slapos_controler.supply(software_path, computer_guid)
      # Here make a request via slapos controler ?
      return {'status_code' : 0}                                          
    else:
      raise ValueError("Too late to supply now. ('self.authorize_supply' is False)")
      return {'status_code' : 1}     

  def _generateInstancetitle(self, test_suite_title):
    """
    Generate an instance title using various parameter
    TODO : add some verification (to don't use unexisting variables)
    """
    instance_title = "Scalability-"
    instance_title += "("+test_suite_title+")-"
    instance_title += str(self.involved_nodes_computer_guid).replace("'","")
    instance_title += "-"
    instance_title += time.strftime('%d/%m/%y_%H:%M:%S',time.localtime())
    return instance_title

  def _generateInstanceXML(self, software_configuration,
                      test_result, test_suite):
    """
    Generate a complete scalability instance XML configuration
    """
    config_cluster = software_configuration.copy()
    config = {'cluster':config_cluster}
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
      self.slapos_controler.request(instance_title, software_path,
                             "scalability", {"_" : config},
                             self.launcher_nodes_computer_guid[0])
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
#      software_path_list = []
#      software_path_list.append(self.testnode.config.get("software_list"))
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
    return self.simulateSlapOSAnswer()
    
  def isInstanceReady(self, instance_title):
    """
    Return true if the specified instance is ready.
    This method should communicates with SlapOS Master.
    """
    # TODO : implement -> communication with SlapOS master
    # this simulate a SlapOS answer
    return self.simulateSlapOSAnswer()
      
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
    self.log("testnode, updateInstanceXML : %s", instance_title)
    self.slapos_controler.updateInstanceXML(instance_title, {"_" : config})
    return {'status_code' : 0} 

  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Install testsuite softwares
    """
    # Define how many time this method can take
    max_time = 3600*10*1.0 # 10 hours
    interval_time = 60
    start_time = time.time()
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
      # create an obfuscated link to the testsuite directory
      path_to_suite = os.path.join(
                      self.testnode.config['working_directory'],
                      node_test_suite.reference)
      self.ofuscated_link_path = os.path.join(
                      self.testnode.config['software_directory'],
                      self.randomized_path)
      if ( not os.path.lexists(self.ofuscated_link_path) and
           not os.path.exists(self.ofuscated_link_path) ) :
        try :
          os.symlink(path_to_suite, self.ofuscated_link_path)
          self.log("testnode, Symbolic link (%s->%s) created."
                   %(self.ofuscated_link_path, path_to_suite))
        except :
          self.log("testnode, Unable to create symbolic link to the testsuite.")
          raise ValueError("testnode, Unable to create symbolic link to the testsuite.")
      self.log("Sym link : %s %s" %(path_to_suite, self.ofuscated_link_path))
      involved_nodes_computer_guid = test_configuration['involved_nodes_computer_guid']
      configuration_list = test_configuration['configuration_list']
      node_test_suite.edit(configuration_list=configuration_list)
      self.launcher_nodes_computer_guid = test_configuration['launcher_nodes_computer_guid']
      software_path_list = []
      # Construct the ipv6 obfuscated url of the software profile reachable from outside
      self.reachable_profile = os.path.join(
        "https://","["+self.testnode.config['httpd_ip']+"]"+":"+self.testnode.config['httpd_software_access_port'],
        self.randomized_path, "software.cfg")
      self.log("Software reachable profile path is : %s "
                              %(self.reachable_profile,))
      software_path_list.append(self.reachable_profile)
      # Ask for softwares installation
      for software_path in software_path_list:
        for computer_guid in self.involved_nodes_computer_guid:
          self._prepareSlapOS(software_path, computer_guid) 
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
        time.sleep(interval_time)
      # TODO : remove the line below wich simulate an answer from slapos master
      self._comeBackFromDummySlapOS()
      if self.remainSoftwareToInstall() :
        # All softwares are not installed, however maxtime is elapsed, that's a failure.
        return {'status_code' : 1}
      self.authorize_request = True
      self.log("Softwares installed")
      """      try:
      """
      # Launch instance
      self.instance_title = self._generateInstancetitle(node_test_suite.test_suite_title)
      self._createInstance(self.reachable_profile, configuration_list[0],
                            self.instance_title, node_test_suite.test_result, node_test_suite.test_suite)
      self.log("Scalability instance requested")
      """      except:
        self.log("Unable to launch instance")
        raise ValueError("Unable to launch instance")
        return {'status_code' : 1} # Unbale to launch instance
      """
      return {'status_code' : 1} # Unable to continue due to not realizable configuration
    return {'status_code' : 0}
  # Used to simulate slapOS answer
  def _waitInstance(self, instance_title):
    self.log("Master testnode is waiting for a (dummy) SlapOS Master answer,\
(kill -10 %s) to continue...", str(os.getpid()))
    self._prepareDummySlapOSAnswer()
    while (not self.isInstanceReady(instance_title)):
      time.sleep(5)
      pass
    self._comeBackFromDummySlapOS()
    self.log("Answer received.")

  def runTestSuite(self, node_test_suite, portal_url):
    if not self.launchable:
      self.log("Current test_suite is not actually launchable.")
      return {'status_code' : 1} # Unable to continue due to not realizable configuration
    configuration_list = node_test_suite.configuration_list
    test_list = range(0, len(configuration_list))
    # create test_result
    test_result_proxy = self.testnode.portal.createTestResult(
      node_test_suite.revision, test_list,
      self.testnode.config['test_node_title'],
      True, node_test_suite.test_suite_title,
      node_test_suite.project_title)
  
    count = 0
    for configuration in configuration_list:
      # Stop instance
      self.slapos_controler.stopInstance(self.instance_title)
      self.log("Waiting for instance stop..")
      self._waitInstance(self.instance_title)
      # Update instance XML configuration 
      self._updateInstanceXML(configuration, self.instance_title,
                      node_test_suite.test_result, node_test_suite.test_suite)
      self.log("Waiting for XML updating instance ready..")
      self._waitInstance(self.instance_title)
      # Start instance
      self.slapos_controler.startInstance(self.instance_title)
      self.log("Waiting for instance start..")
      self._waitInstance(self.instance_title)
      
      # Start only the current test
      exclude_list=[x for x in test_list if x!=test_list[count]]
      count += 1
      test_result_line_proxy = test_result_proxy.start(exclude_list)
      if test_result_line_proxy == None :
        self.log("Already tested.")
        error = ValueError("Test already tested.")
        break;

      # TODO: use only isAlive() and change test_result workflow on ERP5 Master side for the scalability case
      self.log("Test for count : %d is in a running state." %count)
      while test_result_line_proxy.isRunning() and test_result_proxy.isAlive():
        time.sleep(15)
        pass

      # Check test case state
      if test_result_line_proxy.isCompleted():
        self.log("Test case completed.")
        error = None
      elif not test_result_proxy.isAlive():
        self.log("Test cancelled.")
        # Here do somethig with instances
        error = ValueError("Test cancelled")
        break;
      elif test_result_line_proxy.isFailed():
        self.log("Test failed.")
        # Here do somethig with instances
        error = ValueError("Test failed")
        break;
      elif test_result_line_proxy.isCancelled():
        self.log("Test cancelled.")
        # Here do somethig with instances
        error = ValueError("Test has been cancelled")
        break;
      elif test_result_line_proxy.isRunning():
        self.log("Test always running after max time elapsed.")
        # Here do somethig with instances
        error = ValueError("Max time for this test case is elapsed.")
        break;
      else:
        self.log("Test in a undeterminated state.")
        error = ValueError("Test case is in an undeterminated state")
        break;

    
    self.slapos_controler.destroyInstance(self.instance_title)

    
    if error:
      test_result_proxy.fail()
      raise error
    else:
      test_result_proxy.stop()

    return {'status_code' : 0}
    
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
