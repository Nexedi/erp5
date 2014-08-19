##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
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
import tempfile
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
from NodeTestSuite import SlapOSInstance
from Updater import Updater
from Utils import dealShebang
from erp5.util import taskdistribution

class DREAMSimulationRunner():
  def __init__(self, testnode):
    self.testnode = testnode

  def _getSlapOSControler(self, working_directory):
    """
    Create a SlapOSControler for this working dir
    """
    return SlapOSControler.SlapOSControler(
               working_directory,
               self.testnode.config,
               self.testnode.log)

  def _prepareSlapOS(self, working_directory, slapos_instance, log,
          build_software=1, software_path_list=None, **kw):
    """Launch slapos to build software and partitions

    XXX: only build & create partition once for DREAM
    """
    slapproxy_log = os.path.join(self.testnode.config['log_directory'],
                                  'slapproxy.log')
    log('Configured slapproxy log to %r' % slapproxy_log)
    reset_software = slapos_instance.retry_software_count > 10
    if reset_software:
      slapos_instance.retry_software_count = 0
    reset_software = False # Never delete ...
    log('testnode, retry_software_count : %r' % \
             slapos_instance.retry_software_count)

    # XXX Create a new controler because working_directory can be
    #     Different depending of the preparation
    slapos_controler = self._getSlapOSControler(working_directory)

    slapos_controler.initializeSlapOSControler(slapproxy_log=slapproxy_log,
       process_manager=self.testnode.process_manager, reset_software=reset_software,
       software_path_list=software_path_list)

    self.testnode.process_manager.supervisord_pid_file = os.path.join(\
         slapos_controler.instance_root, 'var', 'run', 'supervisord.pid')

    # XXX If all software looks already build, we will not run soft again
    soft_list = glob.glob(os.path.join(
        slapos_instance.working_directory, 'soft', '*'))
    completed_soft_list = glob.glob(os.path.join(
        slapos_instance.working_directory, 'soft', '*', '.completed'))
    if soft_list and len(soft_list) == len(completed_soft_list):
      log('testnode: all software seem built, will not build again')
      build_software = False

    if build_software:
      status_dict = slapos_controler.runSoftwareRelease(
        self.testnode.config,
        environment=self.testnode.config['environment'])
      if status_dict['status_code'] != 0:
         slapos_instance.retry = True
         slapos_instance.retry_software_count += 1
         raise SubprocessError(status_dict)
      slapos_instance.retry_software_count = 0

    status_dict = slapos_controler.runComputerPartition(
        self.testnode.config,
        environment=self.testnode.config['environment'],
        implicit_erp5_config=False)
    if status_dict['status_code'] != 0:
      slapos_instance.retry = True
      slapos_instance.retry_software_count += 1
      raise SubprocessError(status_dict)
    slapos_instance.retry_software_count = 0

    return status_dict

  def prepareSlapOSForTestNode(self, test_node_slapos):
    """
    We will build slapos software needed by the testnode itself,
    like the building of selenium-runner by default
    """
    # I don't think we need that
    return {}
    return self._prepareSlapOS(self.testnode.config['slapos_directory'],
              test_node_slapos, self.testnode.log, create_partition=0,
              software_path_list=self.testnode.config.get("software_list"))

  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Build softwares needed by testsuites
    """
    log = self.testnode.log
    if log is None:
      log = self.testnode.log
    return self._prepareSlapOS(node_test_suite.working_directory,
              node_test_suite, log,
              software_path_list=[node_test_suite.custom_profile_path])

  def runSimulationScenario(self, node_test_suite, portal_url, test_result):
    if not node_test_suite.scenario:
      return # nothing to do

    dream_simulation = glob.glob("%s/inst/*/etc/run/dream_simulation" % \
                node_test_suite.working_directory)[0]
    with tempfile.NamedTemporaryFile() as tf:
        tf.write(json.dumps(json.loads(node_test_suite.scenario)['input']))
        tf.flush()
        invocation_list = [dream_simulation, tf.name]
        status_dict = self.testnode.process_manager.spawn(*invocation_list,
                          cwd=node_test_suite.working_directory,
                          log_prefix='dream_simulation', get_output=True)
        output = status_dict['stdout']

    assert output
    self.testnode.log('Posting back result for %s/%s' % (test_result.test_result_path,
        node_test_suite.test_result_line_id))
    test_result._retryRPC('saveDREAMSimulationResult',
        ('%s/%s' % (test_result.test_result_path, node_test_suite.test_result_line_id),
        output))


  def getRelativePathUsage(self):
    """
    Used by the method testnode.constructProfile() to know
    if the software.cfg have to use relative path or not.
    """
    return False
