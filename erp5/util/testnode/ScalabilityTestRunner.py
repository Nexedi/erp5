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
    A proxy to supply : Install software a software on a specific node
    """
    if self.authorize_supply == True :
      if not(computer_guid in self.remaining_software_installation_grid):
        # Add computer_guid to the grid if it isn't
        self.remaining_software_installation_grid[computer_guid] = []
      self.remaining_software_installation_grid[computer_guid].append(software_path)
      self.slapos_controler.supply(software_path, computer_guid, create_partition)
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
#      for software_path in software_path_list:
#        for launcher_node in self.????_nodes:
#          self._prepareSlapOS(software_path, launcher_node['computer_id']) 
      # TODO : change the line below
      return {'status_code' : 0}   
    else:
      return {'status_code' : 0} 


  def isRemainingSoftwareToInstall(self):
      print self.remaining_software_installation_grid
      return False
      # Here we can 
          
  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Install all testsuite's software
    """
    # In fact we just need to extract (by knowing the ipv6)
    # softwares ipv6-url ( created during constructProfile(...) )
    #software_path_list = _extractSoftwarePathList(software_path_list)
    # TODO : extract software paths (ipv6+local suite path+password?) from node_test_suite
    print "...isValidatedMaster(..):"
    print self.testnode.test_suite_portal.isValidatedMaster(
                           self.testnode.config['test_node_title'])
    test_configuration = testnodeUtils.deunicodeData(
                           json.loads(
                              self.testnode.test_suite_portal.generateConfiguration(
                                node_test_suite.test_suite_title)))
    print "test_configuration:"
    print test_configuration
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
    for software_path in software_path_list:
      for computer_guid in self.involved_nodes_computer_guid:
        self._prepareSlapOS(software_path, computer_guid) 
    # From the line below we would not supply any more softwares
    self.authorize_supply = False
    # Here a loop while softwares are not all installed
    while self.isRemainingSoftwareToInstall() == False:
        self.testnode.log("Master testnode is waiting\
 for the end of all software installation.")
        time.sleep(4)
    
    return {'status_code' : 0}

  def _cleanUpNodesInformation(self):
    self.involved_nodes_computer_guid = []
    self.launcher_nodes_computer_guid = []

  def _generateConfigurationList(self, test_suite): 
    # TODO : implement it 
    return []

  # TODO : define methods to check if involved nodes are okay etc..
  # And if it's not end ans invalidate everything and retry/reloop

  def runTestSuite(self, node_test_suite, portal_url, log=None):
    # TODO : write code
    SlapOSControler.createFolder(node_test_suite.test_suite_directory,
                                 clean=True)
    # create ResultLine for each loop
    
    pass

  def getRelativePathUsage(self):
    return True
