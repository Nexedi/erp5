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

class SlapOSInstance(object):
  """
  Base of an software instance,
  store variables used during software installation
  """
  def __init__(self):
    self.retry_software_count = 0
    self.retry = False

  def edit(self, **kw):
    self.__dict__.update(**kw)
    self._checkData()

  def _checkData(self):
    pass
    
class NodeTestSuite(SlapOSInstance):
  """
  
  """
  def __init__(self, reference):
    super(NodeTestSuite, self).__init__()
    self.reference = reference
    self.cluster_configuration = {}

  def edit(self, **kw):
    super(NodeTestSuite, self).edit(**kw)

  def _checkData(self):
    if getattr(self, "working_directory", None) is not None:
      if not(self.working_directory.endswith(os.path.sep + self.reference)):
        self.working_directory = os.path.join(self.working_directory,
                                             self.reference)
      SlapOSControler.createFolder(self.working_directory)
      self.test_suite_directory = os.path.join(
                                   self.working_directory, "test_suite")
      self.custom_profile_path = os.path.join(self.working_directory,
                                 'software.cfg')
    if getattr(self, "vcs_repository_list", None) is not None:
      for vcs_repository in self.vcs_repository_list:
        buildout_section_id = vcs_repository.get('buildout_section_id', None)
        repository_id = buildout_section_id or \
                        vcs_repository.get('url').split('/')[-1].split('.')[0]
        repository_path = os.path.join(self.working_directory,repository_id)
        vcs_repository['repository_id'] = repository_id
        vcs_repository['repository_path'] = repository_path

  def createSuiteLog(self):
    # /srv/slapgrid/slappartXX/srv/var/log/testnode/az-mlksjfmlk234Sljssdflkj23KSdfslj/suite.log
    alphabets = string.digits + string.letters
    rand_part = ''.join(random.choice(alphabets) for i in xrange(32))
    random_suite_folder_id = '%s-%s' % (self.reference, rand_part)
    suite_log_directory = os.path.join(self.log_directory,
                                       random_suite_folder_id)
    SlapOSControler.createFolders(suite_log_directory)
    # XXX copy the whole content of the log viewer app
    for fname in glob.glob(os.path.join(os.path.dirname(__file__), 'js-logtail', '*')):
      shutil.copy(fname, suite_log_directory)
    self.suite_log_path = os.path.join(suite_log_directory,
                                       'suite.log')
    return self.getSuiteLogPath(), random_suite_folder_id

  def getSuiteLogPath(self):
    return getattr(self,"suite_log_path", None)

  @property
  def revision(self):
    return ','.join('%s=%s-%s' % (
        repository[:-11] if repository.endswith('-repository') else repository,
        count, revision)
      for repository, (count, revision) in self.revision_list)
