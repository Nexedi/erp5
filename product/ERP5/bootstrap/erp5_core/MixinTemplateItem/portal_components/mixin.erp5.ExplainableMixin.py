# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from erp5.component.interface.IExplainable import IExplainable

@zope.interface.implementer(IExplainable,)
class ExplainableMixin:
  """A mixin which provides common implementation of
  IExplainable to simulation movements and applied rules

  TODO:
  - extend it to support Delivery Lines / Cells
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # IExplainable implementation
  security.declareProtected(Permissions.AccessContentsInformation,'getExplanationValueList')
  def getExplanationValueList(self):
    """Returns the list of deliveries of parent simulation
    movements. The first item in the list is the immediate
    explanation value. The last item in the list is the root
    explanation.
    """
    return self._getExplanationValueList()

  def _getExplanationValueList(self, root=False, immediate=False, line=False):
    """Private implementation with some options to optimize and share code
    """
    result = []

    # This implementation does not take into account delivery lines / cells
    # Extension could be obtained by considering getDeliveryRelatedValueList
    document = self

    previous_delivery = None
    still_immediate = True # True if no immediate explanation found yet
    while document.getPortalType() != "Simulation Tool":
      if document.getPortalType() == "Simulation Movement":
        if (not root or (document.getParentValue().getParentValue().getPortalType() == "Simulation Tool"))\
           and (not immediate or still_immediate):
          # Only make an effort to find root delivery if we need
          # to build a complete list of explanations else
          # or if we are at the root of the simulation tree (whenever applies)
          # or if we are at the immediate delivery (whenever applies)
          delivery_line = document.getDeliveryValue()
          if delivery_line is not None:
            if still_immediate: still_immediate = False
            if line:
              result.append(delivery_line)
            else:
              previous_delivery = delivery_line.getRootDeliveryValue()
              result.append(previous_delivery)
      elif document.getPortalType() == "Applied Rule":
        if (not root or (document.getParentValue().getPortalType() == "Simulation Tool"))\
           and (not immediate or still_immediate) and not line:
          # Only make an effort to find root delivery if we need
          # to build a complete list of explanations else
          # or if we are at the root of the simulation tree (whenever applies)
          # or if we are at the immediate delivery (whenever applies)
          # If we collect lines, we do not care about applied rules
          delivery_or_item = document.getCausalityValue()
          if delivery_or_item is not None and delivery_or_item is not previous_delivery:
            if still_immediate: still_immediate = False
            # Make sure not to include same delivery twice
            result.append(delivery_or_item)

      document = document.getParentValue()

    return result

  security.declareProtected(Permissions.AccessContentsInformation,'getRootExplanationValue')
  def getRootExplanationValue(self):
    """Returns the delivery of the root simulation
    movement.
    """
    return self._getExplanationValueList(root=True)[-1]

  security.declareProtected(Permissions.AccessContentsInformation,'getImmediateExplanationValue')
  def getImmediateExplanationValue(self):
    """Returns the delivery of the first parent simulation
    which has a delivery.
    """
    return self._getExplanationValueList(immediate=True)[0]

  security.declareProtected(Permissions.AccessContentsInformation,'getExplanationLineValueList')
  def getExplanationLineValueList(self):
    """Returns the list of delivery lines of parent simulation
    movements. The first item in the list is the immediate
    explanation value. The last item in the list is the root
    explanation.
    """
    return self._getExplanationValueList(line=True)

  security.declareProtected(Permissions.AccessContentsInformation,'getRootExplanationLineValue')
  def getRootExplanationLineValue(self):
    """Returns the delivery line of the root simulation
    movement.
    """
    return self._getExplanationValueList(root=True, line=True)[-1]

  security.declareProtected(Permissions.AccessContentsInformation,'getImmediateExplanationLineValue')
  def getImmediateExplanationLineValue(self):
    """Returns the delivery line of the first parent simulation
    which has a delivery.
    """
    return self._getExplanationValueList(immediate=True, line=True)[0]

  # Compatibility API
  security.declareProtected(Permissions.AccessContentsInformation,'getExplanationUid')
  def getExplanationUid(self):
    """Returns the UID of the root explanation
    """
    return self.getRootExplanationValue().getUid()

InitializeClass(ExplainableMixin)
