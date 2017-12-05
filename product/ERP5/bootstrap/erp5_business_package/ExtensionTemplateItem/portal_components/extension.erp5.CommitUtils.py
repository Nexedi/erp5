##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

def getLatestCommitTitle(commit):
  """
  Function to get last commit title.
  Returns None if there is no last commit
  """
  portal = commit.getPortalObject()
  commit_tool = portal.portal_commits

  # Get all commits in commit tool
  commit_list = commit_tool.objectValues(portal_type='Business Commit')
  # Remove the current created commit from the commit_list
  commit_list = [l for l in commit_list if l != commit]

  # Get the commit which was created last
  latest_commit = max(commit_list, key=lambda x: x.getCreationDate())

  if latest_commit is None:
    return ''
  return latest_commit.getTitle()
