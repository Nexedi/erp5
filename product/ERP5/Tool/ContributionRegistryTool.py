# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool


class ContributionRegistryTool(BaseTool):

  id = 'portal_contribution_registry'
  title = 'Contribution Registry Tool'
  meta_type = 'ERP5 Contribution Registry Tool'
  portal_type = 'Contribution Registry Tool'
  allowed_types = ('ERP5 Contribution Predicate',)

  security = ClassSecurityInfo()

  security.declarePrivate('findPortalTypeName')
  def findPortalTypeName(self, file_name='', mime_type=None, data=None):
    from Products.ERP5Type.Document import newTempIngestionFile
    ingestion_file = newTempIngestionFile(self, 'id')
    ingestion_file._edit(file_name=file_name, mime_type=mime_type, data=data)

    for predicate in self.objectValues(sort_on='int_index'):
      result = predicate.test(ingestion_file)
      if result:
        return result

InitializeClass(ContributionRegistryTool)
