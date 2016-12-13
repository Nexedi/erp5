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
from NodeTestSuite import SlapOSInstance
from Updater import Updater
from Utils import dealShebang
from erp5.util import taskdistribution

class UnitTestRunner():
  def __init__(self, testnode):
    self.testnode = testnode

  def _getSlapOSControler(self, working_directory):
    """
    Create a SlapOSControler
    """
    return SlapOSControler.SlapOSControler(
               working_directory,
               self.testnode.config,
               self.testnode.log)
 

  def _prepareSlapOS(self, working_directory, slapos_instance, log,
          create_partition=1, software_path_list=None, **kw):
    """
    Launch slapos to build software and partitions
    """
    slapproxy_log = os.path.join(self.testnode.config['log_directory'],
                                  'slapproxy.log')
    log('Configured slapproxy log to %r' % slapproxy_log)
    reset_software = slapos_instance.retry_software_count > 10
    if reset_software:
      slapos_instance.retry_software_count = 0
    log('testnode, retry_software_count : %r' % \
             slapos_instance.retry_software_count)

    # XXX Create a new controler because working_directory can be
    #     Diferent depending of the preparation
    slapos_controler = self._getSlapOSControler(working_directory)

    slapos_controler.initializeSlapOSControler(slapproxy_log=slapproxy_log,
       process_manager=self.testnode.process_manager, reset_software=reset_software,
       software_path_list=software_path_list)
    self.testnode.process_manager.supervisord_pid_file = os.path.join(\
         slapos_controler.instance_root, 'var', 'run', 'supervisord.pid')
    method_list= ["runSoftwareRelease"]
    if create_partition:
      method_list.append("runComputerPartition")
    for method_name in method_list:
      slapos_method = getattr(slapos_controler, method_name)
      log("Before status_dict = slapos_method(...)")
      status_dict = slapos_method(self.testnode.config,
                                  environment=self.testnode.config['environment'],
                                  **kw)
      log(status_dict)
      log("After status_dict = slapos_method(...)")
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
    # report-url, report-project and suite-url are required to seleniumrunner
    # instance. This is a hack which must be removed.
    cluster_configuration = {}
    config = self.testnode.config
    cluster_configuration['report-url'] = config.get("report-url", "")
    cluster_configuration['report-project'] = config.get("report-project", "")
    cluster_configuration['suite-url'] = config.get("suite-url", "")
    return self._prepareSlapOS(self.testnode.config['slapos_directory'],
              test_node_slapos, self.testnode.log, create_partition=0,
              software_path_list=self.testnode.config.get("software_list"),
              cluster_configuration=cluster_configuration
              )

  def prepareSlapOSForTestSuite(self, node_test_suite):
    """
    Build softwares needed by testsuites
    """
    log = self.testnode.log
    if log is None:
      log = self.testnode.log
    return self._prepareSlapOS(node_test_suite.working_directory,
              node_test_suite, log,
              software_path_list=[node_test_suite.custom_profile_path],
              cluster_configuration={'_': json.dumps(node_test_suite.cluster_configuration)})

  def runTestSuite(self, node_test_suite, portal_url, log=None):
    config = self.testnode.config
    slapos_controler = self._getSlapOSControler(self.testnode.working_directory)
    run_test_suite_path_list = sorted(glob.glob("%s/*/bin/runTestSuite" % \
        slapos_controler.instance_root))
    if not len(run_test_suite_path_list):
      raise ValueError('No runTestSuite provided in installed partitions.')
    run_test_suite_path = run_test_suite_path_list[0]
    # Deal with Shebang size limitation
    invocation_list = dealShebang(run_test_suite_path)
    invocation_list += (run_test_suite_path,
      '--master_url', portal_url,
      '--revision', node_test_suite.revision,
      '--test_suite', node_test_suite.test_suite,
      '--test_suite_title', node_test_suite.test_suite_title)
    supported_parameter_set = set(self.testnode.process_manager
      .getSupportedParameterList(run_test_suite_path))
    parts = os.path.dirname(os.path.dirname(run_test_suite_path))
    parts += '/software_release/parts/'
    for option in (
        ('--firefox_bin', parts + 'firefox/firefox-slapos'),
        ('--frontend_url', config['frontend_url']),
        ('--node_quantity', config['node_quantity']),
        ('--xvfb_bin', parts + 'xserver/bin/Xvfb'),
        ):
      if option[0] in supported_parameter_set:
        invocation_list += option

    # TODO : include testnode correction ( b111682f14890bf )
    if hasattr(node_test_suite,'additional_bt5_repository_id'):
      additional_bt5_path = os.path.join(
              node_test_suite.working_directory,
              node_test_suite.additional_bt5_repository_id)
      invocation_list.extend(["--bt5_path", additional_bt5_path])
    # From this point, test runner becomes responsible for updating test
    # result. We only do cleanup if the test runner itself is not able
    # to run.
    SlapOSControler.createFolder(node_test_suite.test_suite_directory,
                                 clean=True)
    self.testnode.process_manager.spawn(*invocation_list,
                          cwd=node_test_suite.test_suite_directory,
                          log_prefix='runTestSuite', get_output=False)

  def getRelativePathUsage(self):
    """
    Used by the method testnode.constructProfile() to know
    if the software.cfg have to use relative path or not.
    """
    return False
