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
    # {'COMPX' : ['soft_path1.cfg', 'soft_path2.cfg'],
    #  'COMPY' : ['soft_path1.cfg'], ... }
    self.remaining_software_installation_grid = {}
    # Protection to prevent installation of softwares after checking
    self.still_supply_to_request = True
    
  def checkingSoftwareGrid(self):
      self.still_supply_to_request = False
      # Here we can 
      
  def _prepareSlapOS(self, software_path, computer_guid, create_partition=0):
    # create_partition is kept for compatibility
    """
    A proxy to supply : Install software a software on a specific node
    """
    if self.still_supply_to_request == True :
      if not(computer_guid in self.remaining_software_installation_grid):
        # Add computer_guid to the grid if it isn't
        self.remaining_software_installation_grid[computer_guid] = []
      self.remaining_software_installation_grid[computer_guid].append(software_path)
      self.slapos_controler.supply(software_path, computer_guid, create_partition)
      return {'status_code' : 0}                                          
    else:
      raise ValueError("Too late to supply now. ('self.still_supply_to_request' is False)")
      
  def prepareSlapOSForTestNode(self, test_node_slapos=None):
    """
    We will build slapos software needed by the testnode itself,
    """
    software_path_list = []
    software_path_list.append(self.testnode.config.get("software_list"))
    for software_path in software_path_list:
      for launcher_node in self.launcher_nodes:
        self._prepareSlapOS(software_path, launcher_node['computer_id']) 
    # TODO : change the line below
    return {'status_code' : 0}   
    
  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Install all testsuite's software
    """
    # In fact we just need to extract (by knowing the ipv6)
    # softwares ipv6-url ( created during constructProfile(...) )
    #software_path_list = _extractSoftwarePathList(software_path_list)
    # TODO : extract software paths (ipv6+local suite path+password?) from node_test_suite
    print node_test_suite
    print node_test_suite
    print node_test_suite
    print node_test_suite
    print node_test_suite
    
    

#    self.test_suite_portal.generateConfiguration(node_test_suite)
  
    software_path_list = []
    for software_path in software_path_list:
      for involved_node in self.involved_nodes:
        self._prepareSlapOS(software_path, involved_node['computer_id']) 
    # TODO : change the line below
    return {'status_code' : 0}

  def _cleanUpNodesInformation(self):
    self.worker_nodes = []
    self.launcher_nodes = []

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
