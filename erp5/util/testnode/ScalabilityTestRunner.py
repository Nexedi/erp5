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
    self.involved_nodes = [] # doesn't change during all the test
    self.worker_nodes = [] # may change between two test_suite
    self.launcher_nodes = [] # may change between two test_suite
    self.master_nodes = [] # doesn't change during all the test
    self.slave_nodes = [] # doesn't change during all the test
    
    # remaining_software_installation_grid contains at the begining
    # all the softwares needed for this runner 
    # The grid looks like :
    # { "COMP-1234" : ['http://soft1.cfg', 'https:///ipv6:00/soft2.cfg'],
    #   "COMP-4" : ['http://soft1.cfg', 'https:///ipv6:00/soft3.cfg'],
    #   "COMP-834" : ['http://soft4.cfg'],
    #   "COMP-90" : ['http://soft1.cfg', 'https:///ipv6:00/soft2.cfg'],
    # }
    # A thread is in charge of checking (by communication with slapOS Master)
    # if softwares are correctly installed. If a software is correctly installed,
    # the thread remove the software_url from the grid.
    # The thread never stop his work until he is not killed.
    # In an other hand, the runner (here) loop while the grid is not empty.
    # When the grid is empty, it means that all softwares are installed, so
    # the runner kills the thread and goes to the next procedure step.
    
    # So, it also means that cluster_configuration, cluster_constraint
    # and the list of availables/involved nodes (=> software repartition)
    # have to be known to fill the grid.
    self.remaining_software_installation_grid = {}
    

  def _prepareSlapOS(self, software_path, computer_guid, create_partition=0):
    # create_partition is kept for compatibility
    """
    A proxy to supply : Install software a software on a specific node
    """ 
    self.slapos_controler.supply(software_path, computer_guid, create_partition)
    # TODO : do something with slapOS Master to check if it's ok
    # put it here ?
    # TODO : change the line below
    return {'status_code' : 0}                                          
  
  def prepareSlapOSForTestNode(self, test_node_slapos=None):
    """
    Install all softwares used to run tests (ex : launcher software)
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
    Install all testsuite's softwares (on worker_nodes)
    """
    # In fact we just need to extract (by knowing the ipv6)
    # softwares ipv6-url ( created during constructProfile(...) )
    #software_path_list = _extractSoftwarePathList(software_path_list)
    # TODO : extract software paths (ipv6+local suite path+password?) from node_test_suite
    software_path_list = []
    for software_path in software_path_list:
      for worker_node in self.worker_nodes:
        self._prepareSlapOS(software_path,worker_node['computer_id']) 
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
    pass


  def getRelativePathUsage(self):
    return True
