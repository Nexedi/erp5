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

import six
from Products.ERP5Type.Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from Products.PythonScripts.Utility import allow_class
if 1: # BBB
  import zLOG, sys
  zLOG.LOG('Products.ERP5Type.Messages',
      zLOG.INFO,
      'Products.PageTemplates.GlobalTranslationService has been removed. '
      'Using alternative implementation',)
  import zope.i18n
  from zope.i18n.interfaces import ITranslationDomain
  from Acquisition import aq_get

  class GlobalTranslationService(object):
    """ GlobalTranslationService replacement """
    # inspired by the old Localizer GlobalTranslationService

    def getTranslateMethod(self, context, domain):
        """Returns either the translate() method of an appropriate Localizer
        MessageCatalog or zope.i18n.translate
        """
        if context is None:
            return zope.i18n.translate
        # Try to get a catalog from a Localizer Object using acquisition
        # FIXME: This should be fixed to use queryUtility instead, but only
        # after ERP5Site starts implementing ISite so that MessageCatalogs can
        # registerm themselves as local utilities.
        # translation_domain = zope.component.getUtility(ITranslationDomain,
        #                                                domain,
        #                                                context=context)
        translation_domain = context.unrestrictedTraverse(("Localizer", domain),
                                                          None)
        # FIXME: Remove this check once we're using getUtility
        if ITranslationDomain.providedBy(translation_domain):
            return translation_domain.translate
        # Localizer above does not like the 'domain' keyword, but zope.i18n
        # needs it.
        def translate(**kw):
          return zope.i18n.translate(domain=domain, **kw)
        return translate

    def translate(self, domain, msgid, context=None, **kw):
        translate = self.getTranslateMethod(context, domain)

        # For zope.i18n, the 'context' of a translation request is actually the
        # an IBrowserRequest, for languate negotiation (see, for instance,
        # Products.CMFPlone.TranslationServiceTool). The new localizer
        # MessageCatalog abides by the zope.i18n.interface definitions.
        # (Actually, it ignores the context).
        request = aq_get(context, 'REQUEST', None)
        return translate(msgid=msgid, context=request, **kw)

  getGlobalTranslationService = GlobalTranslationService

from Products.ERP5Type import Globals
from string import Template
from base64 import b64encode, b64decode

class Message(Persistent):
  """
  This class encapsulates message, mapping and domain for a given message
  """

  security = ClassSecurityInfo()
  security.declareObjectPublic()

  def __init__(self, domain=None, message='',
               mapping=None, default=None):
    self.message = message
    if mapping is not None:
      assert isinstance(mapping, dict)
    self.mapping = mapping
    self.domain = domain
    if default is None:
      default = message
    self.default = default

  def translate(self):
    """
    Return the translated message. If the original is a string object,
    the return value is a string object. If it is a unicode object,
    the return value is a unicode object.
    """
    message = self.message
    if self.domain is None:
      # Map the translated string with given parameters
      if type(self.mapping) is dict:
        if six.PY2 and isinstance(message, six.text_type) :
          message = message.encode('utf-8')
        message = Template(message).substitute(self.mapping)
    else:
      from Products.ERP5.ERP5Site import getSite
      request = Globals.get_request()
      translation_service = getGlobalTranslationService()
      if self.mapping:
        unicode_mapping = {}
        for k, v in six.iteritems(self.mapping):
          if six.PY2 and isinstance(v, str):
            v = v.decode('utf-8')
          unicode_mapping[k] = v
      else:
        unicode_mapping = self.mapping
      translated_message = translation_service.translate(
                                             self.domain,
                                             message,
                                             mapping=unicode_mapping,
                                             context=getSite(request),
                                             default=self.default)
      if translated_message is not None:
        message = translated_message

    if isinstance(self.message, str):
      if six.PY2 and isinstance(message, six.text_type):
        message = message.encode('utf-8')
    elif six.PY2 and isinstance(message, str):
      message = message.decode('utf-8')

    return message

  def __repr__(self):
    return "<ERP5Type.Message.Message for %r>" % self.message

  def __str__(self):
    """
    Return the translated message as a string object.
    """
    message = self.translate()
    if six.PY2 and isinstance(message, six.text_type):
      message = message.encode('utf-8')
    return message

  def __unicode__(self):
    """
    Return the translated message as a unicode object.
    """
    message = self.translate()
    if six.PY2 and isinstance(message, str):
      message = message.decode('utf-8')
    return message

  def __len__(self):
    return len(str(self))

  def __getitem__(self, index):
    return str(self)[index]

  def __getslice__(self, i, j):
    return str(self)[i:j]

InitializeClass(Message)
allow_class(Message)


def translateString(message, **kw):
  return Message(domain='erp5_ui', message=message, **kw)
