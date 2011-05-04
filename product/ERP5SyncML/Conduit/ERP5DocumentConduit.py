# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@gmail.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5SyncML.Conduit.ERP5Conduit import ERP5Conduit
from Products.ERP5Type import Permissions
from AccessControl import ClassSecurityInfo
from StringIO import StringIO

# Declarative security
security = ClassSecurityInfo()

class ERP5DocumentConduit(ERP5Conduit):
  """
  ERP5DocumentConduit specialise generic Conduit
  to produce adhoc GID.
  The GID is composed by the concatenation of "reference-version-language"
  """

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'getGidFromObject')
  def getGidFromObject(self, object):
    """
    return the Gid generate with the reference, object, language of the object
    """
    return "%s-%s-%s" %\
             (object.getReference(), object.getVersion(), object.getLanguage())

