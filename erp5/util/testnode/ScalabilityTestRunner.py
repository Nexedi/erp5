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
import testnodeUtils
from ProcessManager import SubprocessError, ProcessManager, CancellationError
from subprocess import CalledProcessError
from Updater import Updater
from erp5.util import taskdistribution



class ScalabilityTestRunner():
  def __init__(self, testnode):
    self.testnode =  testnode
    self.slapos_controler = SlapOSControler.SlapOSControler(
                                  self.testnode.working_directory,
                                  self.testnode.config,
                                  self.testnode.log)
    # Create the slapos account configuration file and dir
    key = self.testnode.test_suite_portal.getSlaposAccountKey()
    certificate = self.testnode.test_suite_portal.getSlaposAccountCertificate()
    self.slapos_controler.createSlaposConfigurationFileAccount(key,certificate,
                                    self.testnode.config, self.testnode.log)
    
    # {'COMPX' : ['soft_path1.cfg', 'soft_path2.cfg'],
    #  'COMPY' : ['soft_path1.cfg'], ... }
    self.remaining_software_installation_grid = {}
    # Protection to prevent installation of softwares after checking
    self.authorize_supply = True
    
      
  def _prepareSlapOS(self, software_path, computer_guid, create_partition=0):
    # create_partition is kept for compatibility
    """
    A proxy to supply : Install a software on a specific node
    """
    self.testnode.log("TESTNODE SUPPLY : %s %s", software_path, computer_guid)
    if self.authorize_supply == True :
      if not(computer_guid in self.remaining_software_installation_grid):
        # Add computer_guid to the grid if it isn't
        self.remaining_software_installation_grid[computer_guid] = []
      self.remaining_software_installation_grid[computer_guid].append(software_path)
      self.slapos_controler.supply(software_path, computer_guid)
      # Here make a request via slapos controler ?
      return {'status_code' : 0}                                          
    else:
      raise ValueError("Too late to supply now. ('self.authorize_supply' is False)")
      
  def prepareSlapOSForTestNode(self, test_node_slapos=None):
    """
    We will build slapos software needed by the testnode itself,
    """
    if self.testnode.test_suite_portal.isValidatedMaster(
                           self.testnode.config['test_node_title']):
#      software_path_list = []
#      software_path_list.append(self.testnode.config.get("software_list"))
    return {'status_code' : 0} 

  def remainSoftwareToInstall(self):
      # Check SlapOS Master to know if softwares are ready
      # and remove from self.remaining_software_installation_grid
      # installed softwares.
      print self.remaining_software_installation_grid
      return True
          
  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Install testsuite softwares
    """
    # Define how many time this method can take
    max_time = 3600*10 # 10 hours
    start_time = time.time()
    # 
    if self.testnode.test_suite_portal.isValidatedMaster(
                           self.testnode.config['test_node_title']):
        # Get from ERP5 Master the configuration of the cluster for the test
        test_configuration = testnodeUtils.deunicodeData(
                               json.loads(
                                  self.testnode.test_suite_portal.generateConfiguration(
                                    node_test_suite.test_suite_title)))
        self.involved_nodes_computer_guid = test_configuration['involved_nodes_computer_guid']
        self.launchable = test_configuration['launchable']
        self.error_message = test_configuration['error_message']
        if self.launchable == False:
          self.testnode.log("Test suite %s is not actually launchable with \
    the current cluster configuration." %(node_test_suite.test_suite_title,))
          self.testnode.log("ERP5 Master indicates : %s" %(self.error_message,))

          # wich code to return ?
          return {'status_code' : 1}
        involved_nodes_computer_guid = test_configuration['involved_nodes_computer_guid']
        configuration_list = test_configuration['configuration_list']
        launcher_nodes_computer_guid = test_configuration['launcher_nodes_computer_guid']
      
        software_path_list = []
        # Here add the ipv6 url reachable from master profile
        software_path_list.append("http://foo.bar/It_is_a_test_for_scalability_test/My_unreachable_profile.cfg")
        # Ask for softwares installation
        for software_path in software_path_list:
          for computer_guid in self.involved_nodes_computer_guid:
            self._prepareSlapOS(software_path, computer_guid) 
        # From the line below we would not supply any more softwares
        self.authorize_supply = False
        # Waiting until all softwares are installed
        while (self.remainSoftwareToInstall() == True)
           and (max_time <= time.time()-start_time):
            self.testnode.log("Master testnode is waiting\
     for the end of all software installation.")
            time.sleep(15)
        # We were wainting for too long time, that's a failure.
        if self.isRemainingSoftwareToInstall() == False:
          return {'status_code' : 1}
    return {'status_code' : 0}

  def _cleanUpNodesInformation(self):
    self.involved_nodes_computer_guid = []
    self.launcher_nodes_computer_guid = []

  def runTestSuite(self, node_test_suite, portal_url, log=None):
    # TODO : write code
    SlapOSControler.createFolder(node_test_suite.test_suite_directory,
                                 clean=True)
    # create ResultLine for each loop    
    pass

  def getRelativePathUsage(self):
    return True
