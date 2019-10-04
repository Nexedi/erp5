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
import errno
import os
import glob
import shutil
import string
import random
from .Utils import createFolder

from six.moves import range

class SlapOSInstance(object):
  """
  Base of an software instance,
  store variables used during software installation
  """
  def __init__(self, working_directory):
    self.retry_software_count = 0
    self.retry = False
    self.working_directory = working_directory


class NodeTestSuite(SlapOSInstance):
  """
  
  """
  def __init__(self, reference, working_directory):
    self.test_node_working_directory = working_directory
    d = os.path.join(working_directory, reference)
    super(NodeTestSuite, self).__init__(d)
    self.reference = reference
    self.cluster_configuration = {}
    self.test_suite_directory = os.path.join(d, 'test_suite')
    self.custom_profile_path = os.path.join(d, 'software.cfg')
    createFolder(d)

  def edit(self, **kw):
    self.__dict__.update(**kw)
    for vcs_repository in kw.get('vcs_repository_list', ()):
        buildout_section_id = vcs_repository.get('buildout_section_id')
        repository_id = buildout_section_id or \
                        vcs_repository.get('url').split('/')[-1].split('.')[0]
        repository_path = os.path.join(self.working_directory,repository_id)
        vcs_repository['repository_id'] = repository_id
        vcs_repository['repository_path'] = repository_path

  def createSuiteLog(self):
    # /srv/slapgrid/slappartXX/srv/var/log/testnode/az-D27KqX7FxJ/suite.log
    alphabets = string.digits + string.ascii_letters
    while 1:
      log_folder_name = '%s-%s' % (self.reference,
        ''.join(random.choice(alphabets) for i in range(10)))
      self.log_folder_path = os.path.join(self.log_directory, log_folder_name)
      try:
        os.makedirs(self.log_folder_path)
      except OSError as e:
        if e.errno != errno.EEXIST:
          raise
      else:
        break
    # XXX copy the whole content of the log viewer app
    for fname in glob.glob(os.path.join(os.path.dirname(__file__), 'js-logtail', '*')):
      shutil.copy(fname, self.log_folder_path)
    self.suite_log_path = os.path.join(self.log_folder_path, 'suite.log')
    return self.suite_log_path, log_folder_name

  @property
  def revision(self):
    return ','.join('%s=%s-%s' % (
        repository[:-11] if repository.endswith('-repository') else repository,
        count, revision)
      for repository, (count, revision) in self.revision_list)
