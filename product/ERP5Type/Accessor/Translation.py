##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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

from Base import func_code, ATTRIBUTE_PREFIX, Method, evaluateTales
from zLOG import LOG
from Products.ERP5Type.PsycoWrapper import psyco
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

class TranslatedPropertyGetter(Method):
  """
  Get the translated property
  """
  _need__name__=1

  # This can be called from the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, warning=0):
    self._id = id
    self.__name__ = id
    self._key = key
    self._original_key = key.replace('translated_', '')
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    if self._warning:
      LOG("ERP5Type Deprecated Getter Id:",0, self._id)
    domain = instance.getProperty('%s_translation_domain' %
                                  self._original_key)
    value = instance.getProperty(self._original_key)
    if domain == '' or (value in ('', None)):
      return value
    localizer = getToolByName(instance, 'Localizer')
    return localizer[domain].gettext(unicode(value, 'utf8')).encode('utf8')

  psyco.bind(__call__)


class PropertyTranslationDomainGetter(Method):
  """
  Get the translation domain
  """
  _need__name__=1

  # This can be called from the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, property_type, default=None, storage_id=None):
    self._id = id
    self.__name__ = id
    self._key = key
    self._original_key = key.replace('_translation_domain', '')
    self._property_type = property_type
    self._default = default
    if storage_id is None:
      storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
    self._storage_id = storage_id
    self._is_tales_type = (property_type == 'tales')

  def __call__(self, instance, *args, **kw):
    if len(args) > 0:
      default = args[0]
    else:
      default = self._default
    # No acquisition on properties
    value = getattr(aq_base(instance), self._storage_id, None)
    if value is None:
      # second try to get it from portal type
      ptype_domain = None
      ptype = instance.getPortalType()
      ptypes_tool = instance.getPortalObject()['portal_types']
      typeinfo = ptypes_tool.getTypeInfo(ptype)
      if typeinfo is None:
        ptype_domain = ''
      else:
        domain_dict = typeinfo.getPropertyTranslationDomainDict()
        domain = domain_dict.get(self._original_key)
        if domain is None:
          ptype_domain = ''
        else:
          ptype_domain = domain.getDomainName()
      if ptype_domain is '' and default is not None:
        # then get the default property defined on property sheet
        value = default
      else:
        value = ptype_domain
    if value is None:
      value = ''
    if self._is_tales_type and kw.get('evaluate', 1):
      return evaluateTales(instance, value)
    else:
      return value

  psyco.bind(__call__)


