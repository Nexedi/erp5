# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
from erp5.component.module.DivergenceMessage import DivergenceMessage
from Products.ERP5Type.Message import Message
from Products.PythonScripts.standard import html_quote as h
from zLOG import LOG, WARNING
from erp5.component.interface.IEquivalenceTester import IEquivalenceTester

@zope.interface.implementer(IEquivalenceTester,)
class EquivalenceTesterMixin:
  """
  Provides generic methods and helper methods to implement
  IEquivalenceTester
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Implementation of IEquivalenceTester
  security.declarePrivate('testEquivalence')
  def testEquivalence(self, simulation_movement):
    """
    Tests if simulation_movement is divergent. Returns False (0)
    or True (1).

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.

    simulation_movement -- a simulation movement
    """
    return self.explain(simulation_movement) is not None

  security.declarePrivate('explain')
  def explain(self, simulation_movement):
    """
    Returns a single message which explain the nature of
    the equivalence of simulation_movement with its related
    delivery movement.

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.

    simulation_movement -- a simulation movement

    NOTE: this approach is incompatible with previous
    API which was returning a list.

    NOTE: should we provide compatibility here ?
    """
    delivery_movement = simulation_movement.getDeliveryValue()
    compare_result = self._compare(simulation_movement, delivery_movement)
    if compare_result is None:
      return None
    else:
      prevision_value, decision_value, message, mapping = compare_result
      return DivergenceMessage(
        object_relative_url=delivery_movement.getRelativeUrl(),
        simulation_movement=simulation_movement,
        decision_value=decision_value,
        prevision_value=prevision_value,
        tested_property=self.getTestedProperty(),
        tester_relative_url=self.getRelativeUrl(),
        message=message,
        mapping=mapping
        )

  @staticmethod
  def _getTestedPropertyValue(movement, property): # pylint: disable=redefined-builtin
    """
    Getter returning the value for the given tested property
    """
    return movement.getProperty(property)

  security.declarePrivate('generateHashKey')
  def generateHashKey(self, movement):
    """
    Returns a hash key which can be used to optimise the
    matching algorithm between movements. The purpose
    of this hash key is to reduce the size of lists of
    movements which need to be compared using the compare
    method (quadratic complexity).

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.
    """
    tested_property = self.getTestedProperty()
    if movement.isPropertyRecorded(tested_property):
      value = movement.getRecordedProperty(tested_property)
    else:
      value = self._getTestedPropertyValue(movement, tested_property)
    return '%s/%r' % (tested_property, value)

  security.declarePrivate('compare')
  def compare(self, prevision_movement, decision_movement):
    """
    Returns True if prevision_movement and delivery_movement
    match. Returns False otherwise. The method is asymmetric and
    the order of parameters matters. For example, a sourcing
    rule may use a tester which makes sure that movements are
    delivered no sooner than 2 weeks before production but
    no later than the production date.

    If decision_movement is a simulation movement, use
    the recorded properties instead of the native ones.

    This method is used in three cases:
    * an applied rule containted movement vs. a generated movement list
    * a delivery containted movement vs. a generated movement list
    * a delivery containted movement vs. an applied rule containted movement
    """
    return (self._compare(prevision_movement, decision_movement) is None)

  security.declarePrivate('update')
  def update(self, prevision_movement, decision_movement):
    """
    Updates decision_movement with properties from
    prevision_movement so that next call to
    compare returns True. This method is normally
    invoked to copy properties from simulation movements
    to delivery movements. It is also invoked to copy
    properties from temp simulation movements of
    Aggregated Amount Lists to pre-existing simulation
    movements.

    If decision_movement is a simulation movement, then
    do not update recorded properties.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)

    NOTE: recorded (forced) properties are not updated by
    expand.

    NOTE2: it is still unknown how to update properties from
    a simulation movement to the relevant level of
    delivery / line / cell.
    """
    decision_movement.edit(
      **self.getUpdatablePropertyDict(prevision_movement, decision_movement))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExplanationMessage')
  def getExplanationMessage(self, simulation_movement):
    """
    Returns the HTML message that describes the detail of the
    divergence.
    """
    divergence_message = self.explain(simulation_movement)
    if divergence_message is None:
      return None
    # XXX explanation message should be provided by each class, each
    # portal type or each document.
    introduction_message = 'On <a href="${decision_url}">${decision_type} ${decision_title}</a> '\
               'of <a href="${delivery_url}">${delivery_title}</a> : '
    decision_movement = self.getPortalObject().unrestrictedTraverse(
      divergence_message.getProperty('object_relative_url'))
    decision_delivery = decision_movement.getRootDeliveryValue()
    introduction_mapping = {
      'decision_url':decision_movement.absolute_url(),
      'decision_type':decision_movement.getTranslatedPortalType(),
      'decision_title':h(decision_movement.getTitleOrId()),
      'delivery_url':decision_delivery.absolute_url(),
      'delivery_title':h(decision_delivery.getTitleOrId()),
      'prevision_url':'#', # XXX it should be a link to the detailed view.
                           # For example, we might want to show a partial view of
                           # the original order associated with partial view of
                           # related packing list
      }
    message = divergence_message.getProperty('message')
    mapping = dict([(x, h(y)) for (x,y) in divergence_message.getProperty('mapping', {}).items()])
    return str(Message(domain='erp5_ui', message=introduction_message,
               mapping=introduction_mapping)) \
           + str(Message(domain='erp5_ui', message=message, mapping=mapping))

  # Placeholder for methods to override
  def _compare(self, prevision_movement, decision_movement):
    """
    If prevision_movement and decision_movement don't match, it returns a
    list : (prevision_value, decision_value, message, mapping)
    """
    raise NotImplementedError

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getUpdatablePropertyDict')
  def getUpdatablePropertyDict(self, prevision_movement, decision_movement):
    """
    Returns a mapping of properties to update on decision_movement so that next
    call to compare against prevision_movement returns True.

    prevision_movement -- a simulation movement (prevision)

    decision_movement -- a delivery movement (decision)
    """
    tested_property = self.getTestedProperty()
    return {tested_property: self._getTestedPropertyValue(prevision_movement,
                                                          tested_property)}

  # Temporary compatibility code that will fix existing data.
  # This Code must be removed in 2 years (end of 2017)
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTestedProperty')
  def getTestedProperty(self):
    """
    Override getTestedProperty to fix the way it is stored. Some time
    ago it was multi-valued, which is non-sense we the implementation we
    have on this equivalence tester.
    """
    tested_property = getattr(self, 'tested_property', None)
    if (getattr(self, '_baseGetTestedPropertyList', None) is None and
        isinstance(tested_property, tuple)):
      if len(tested_property) == 1:
        new_value = tested_property[0]
      else:
        new_value = None

      setattr(self, 'tested_property', new_value)
      LOG("equivalence_tester", WARNING,
          "%s: Migrated tested_property: %r => %r" % (self.getRelativeUrl(),
                                                      tested_property,
                                                      new_value))

    return self._baseGetTestedProperty()

  def getTestedPropertyList(self):
    if getattr(self, '_baseGetTestedPropertyList', None) is None:
      return [self.getTestedProperty()]

    return self._baseGetTestedPropertyList()

  def getTestedPropertyTitle(self):
    tested_property_title = getattr(self, 'tested_property_title', None)
    if (getattr(self, '_baseGetTestedPropertyTitleList', None) is None and
        isinstance(tested_property_title, tuple)):
      if len(tested_property_title) == 1:
        new_value = tested_property_title[0]
      else:
        new_value = None

      setattr(self, 'tested_property_title', new_value)
      LOG("equivalence_tester", WARNING,
          "%s: Migrated tested_property_title: %r => %r" % (self.getRelativeUrl(),
                                                            tested_property_title,
                                                            new_value))

    return self._baseGetTestedPropertyTitle()

  def getTestedPropertyTitleList(self):
    if getattr(self, '_baseGetTestedPropertyTitleList', None) is None:
      return [self.getTestedPropertyTitle()]

    return self._baseGetTestedPropertyTitleList()

InitializeClass(EquivalenceTesterMixin)
