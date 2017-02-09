# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ayush-Tiwari <ayush.tiwari@nexedi.com>
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

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import Persistent
from Acquisition import Implicit, aq_base, aq_inner, aq_parent

class BusinessTemplate(XMLObject):
    """
    Business Template is responsible for saving objects and properties in
    an ERP5Site. Everything will be saved just via path
    """
    meta_type = 'ERP5 Business Template'
    portal_type = 'Business Template'
    allowed_content_types = ('BusinessItem', )
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)


    def __init__(self, *args, **kw):
      pass

class BusinessItem(Implicit, Persistent):
    """
      Saves the path and values for objects, properties, etc, the
      attributes for a path configuration being:

      - path  (similar to an xpath expression)
      - sign  (+1/-1)
      - layer (0, 1, 2, 3, etc.)
      - value (a set of pickable value in python)
    """

    def __init__(self, *args, **kw):
      self.path = path
      self.sign = 1               # should be int or bool ??
      self.layer = layer          # should be int
      self.value = value          # should be hash of value at the path
