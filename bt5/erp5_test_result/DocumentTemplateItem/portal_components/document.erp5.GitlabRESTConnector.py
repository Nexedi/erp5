# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2019 Nexedi SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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


from urllib import quote_plus
from urlparse import urlparse
from urlparse import urljoin
import logging

from AccessControl import ClassSecurityInfo
import requests

from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.XMLObject import XMLObject


class GitlabRESTConnector(XMLObject):
  """Connects to gitlab v4 REST API.
  """
  logger = logging.getLogger(__name__)
  security = ClassSecurityInfo()

  def _getRepositoryIdFromRepositoryUrl(self, repository_url):
    # repository_url will be https://lab.nexedi.com/user/project.git
    # convert this to user%2fproject
    username_repo = urlparse(repository_url).path[1:] # remove leading /
    if username_repo.endswith('/'):
      username_repo = username_repo[:-1]
    if username_repo.endswith('.git'):
      username_repo = username_repo[:-4]
    return quote_plus(username_repo)

  security.declareProtected(
      Permissions.AccessContentsInformation,
      'postCommitStatus')
  def postCommitStatus(self, repository_url, commit_sha, state, target_url, name):
    """Post the build status of a commit.

    https://docs.gitlab.com/ce/api/commits.html#post-the-build-status-to-a-commit
    """
    url = urljoin(
        self.getUrlString(),
        "projects/{id}/statuses/{sha}".format(
            id=self._getRepositoryIdFromRepositoryUrl(repository_url),
            sha=commit_sha
        )
    )
    self.logger.info("posting commit status to %s", url)
    response = requests.post(
      url,
      headers={"PRIVATE-TOKEN": self.getToken()},
      json={
          "state": state,
          "target_url": target_url,
          "name": name
      },
      timeout=5)

    if response.status_code == requests.codes.not_found and\
       response.json()['message'] == "404 References for commit Not Found":
      # It can happen that commit is not found, for example when test start
      # on a commit and later this commit is no longer reachable from any
      # branch. This typically happen after a new commit was push-forced to
      # the tested branch.
      return
    response.raise_for_status()


InitializeClass(GitlabRESTConnector)
