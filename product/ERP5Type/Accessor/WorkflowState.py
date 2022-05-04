from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.ERP5Type.Utils import unicode2str
from Acquisition import aq_base
from Products.ERP5Type.PsycoWrapper import psyco
from .Base import Getter as BaseGetter, Setter as BaseSetter
from warnings import warn

# Creation of default constructor
class func_code: pass

class Getter(BaseGetter):
    """
      Gets an attribute value. A default value can be
      provided if needed
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self',)
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance):
      portal_workflow = instance.getPortalObject().portal_workflow
      wf = portal_workflow._getOb(self._key)
      return wf._getWorkflowStateOf(instance, id_only=1)

    psyco.bind(__call__)

class TitleGetter(BaseGetter):
    """
      Gets the title of the current state
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    __code__ = func_code = func_code()
    __code__.co_varnames = ('self',)
    __code__.co_argcount = 1
    __defaults__ = func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance):
      portal_workflow = instance.getPortalObject().portal_workflow
      wf = portal_workflow._getOb(self._key)
      return wf._getWorkflowStateOf(instance).title

    psyco.bind(__call__)

class TranslatedGetter(Getter):
    """ returns the workflow state ID transated. DEPRECATED
    """

    def __call__(self, instance):
      portal = instance.getPortalObject()
      wf = portal.portal_workflow._getOb(self._key)
      state_id = wf._getWorkflowStateOf(instance, id_only=1)
      warn('Translated workflow state getters, such as %s are deprecated' %
            self._id, DeprecationWarning)
      return unicode2str(portal.Localizer.erp5_ui.gettext(state_id))

    psyco.bind(__call__)

class TranslatedTitleGetter(TitleGetter):
    """
      Gets the translated title of the current state
    """

    def __call__(self, instance):
      portal = instance.getPortalObject()
      localizer = portal.Localizer
      wf_id = self._key
      wf = portal.portal_workflow._getOb(wf_id)
      selected_language = localizer.get_selected_language()
      state_title = wf._getWorkflowStateOf(instance).title
      msg_id = '%s [state in %s]' % (state_title, wf_id)
      result = localizer.erp5_ui.gettext(msg_id,
                                         lang=selected_language,
                                         default='')
      if result == '':
        result = localizer.erp5_ui.gettext(state_title,
                                           lang=selected_language)
      return unicode2str(result)

    psyco.bind(__call__)

def SerializeGetter(id, key):
  def serialize(self):
    """Prevent concurrent transaction from changing of state of this object
    """
    try:
      self = aq_base(self).workflow_history
      self = self[key]
    except (AttributeError, KeyError):
      pass
    self._p_changed = 1
  serialize.__name__ = id
  return serialize
