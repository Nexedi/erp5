##############################################################################
# -*- coding: utf8 -*-
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                Aurélien Calonne <aurel@nexedi.com>
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
from Products.ERP5Type import PropertySheet, Permissions, Interface
from Globals import InitializeClass
from Products.ERP5.Document.Predicate import Predicate


class Archive(Predicate):
  """
  A Catalog Archive object

  It defines the date of the archive and the catalog to use
  """

  meta_type = 'ERP5 Archive'
  portal_type = 'Archive'
  isPortalContent = 1
  isRADContent = 1
  
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = ( Interface.Predicate, )

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.Archive
                    )
  
  isIndexable = 1
    

InitializeClass(Archive)
