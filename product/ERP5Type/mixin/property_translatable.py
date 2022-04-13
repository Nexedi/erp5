##############################################################################
#
# Copyright (c) 2009 Nexedi KK, Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
from Products.ERP5Type.interfaces.property_translatable import IPropertyTranslatable
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass


INTERNAL_TRANSLATION_DICT_NAME = '__translation_dict'

@zope.interface.implementer(IPropertyTranslatable)
class PropertyTranslatableBuiltInDictMixIn:
  """An implementation of IPropertyTranslatable with built-in dict."""

  security = ClassSecurityInfo()

  def _getTranslationDict(self, create_if_missing=False):
    """
    create_if_missing: force creation of translation dict. It is false by
                       default to havoid zodb pollution when only try to get
                       translations
    """
    try:
      return getattr(self, INTERNAL_TRANSLATION_DICT_NAME)
    except AttributeError:
      dict_ = {}
      if create_if_missing:
        setattr(self, INTERNAL_TRANSLATION_DICT_NAME, dict_)
        self._p_changed = True
      return dict_

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyTranslation')
  def getPropertyTranslation(self, property_id, language):
    return self._getTranslationDict()[(property_id, language)][1]

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setPropertyTranslation')
  def setPropertyTranslation(self, property_id, language, original_text, translation):
    self._getTranslationDict(create_if_missing=True)[(property_id, language)] = \
          (original_text, translation)
    self._p_changed = True

  security.declareProtected(Permissions.ModifyPortalContent,
                            'deletePropertyTranslation')
  def deletePropertyTranslation(self, property_id, language):
    try:
      del self._getTranslationDict()[(property_id, language)]
      self._p_changed = True
    except KeyError:
      pass

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPropertyTranslationOriginalText')
  def getPropertyTranslationOriginalText(self, property_id, language):
    return self._getTranslationDict()[(property_id, language)][0]

  security.declareProtected(Permissions.AccessContentsInformation,
                          'isPropertyTranslated')
  def isPropertyTranslated(self, property_id, language):
    try:
      self._getTranslationDict()[(property_id, language)]
      return True
    except KeyError:
      return False

InitializeClass(PropertyTranslatableBuiltInDictMixIn)
