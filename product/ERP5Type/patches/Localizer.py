##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# Template() is a new method of python 2.4, that's why we have the string.py
#   file in patches directory.
try:
  from string import Template
except ImportError:
  from Products.ERP5Type.patches.string import Template

from Products.ERP5Type.Message import Message
from zLOG import LOG, ERROR

class LocalizerPatchError(Exception):
  """Error wen trying to use or apply the Localizer patch"""

# This patch will not work if Translation Service Zope product exist on the system
try:
  from Products import TranslationService
  LOG("ERP5Type.patches.Localizer", ERROR, "Translation Service Zope Product"
      " (%s) and Translation Service tools must be deleted to let Localizer "
      "Patch work." % (repr(TranslationService)))
except ImportError:
  pass


def Localizer_translate(self, domain, msgid, lang=None, mapping=None, *args, **kw):
    """
      This translate() method use Localizer and support catalog aliases.
    """
    # This dict define the alias between old Translation Service catalog id
    #   and new Localizer Message Catalog.
    message_catalog_aliases = { "Default": "default"
                              , "ui"     : "erp5_ui"
                              , "content": "erp5_content"
                              }

    # Get the Localizer catalog id
    catalog_id = message_catalog_aliases.get(domain, domain)
    catalog_obj = self._getOb(catalog_id, None)
    if catalog_obj is None:
      # No catalog found: use the default one
      catalog_obj = self['default']

    # Call the Message Catalog gettext method
    params = {}
    for key in ('add', 'default'):
      try:
        params[key] = kw[key]
      except KeyError:
        pass
    if lang is not None:
      params['lang'] = lang
    else:
      try:
        params['lang'] = kw['target_language']
      except KeyError:
        pass
    translated_str = catalog_obj.gettext(msgid, **params)

    # Map the translated string with given parameters
    if isinstance(mapping, dict) and mapping:
      unicode_mapping = {}
      if not isinstance(translated_str, unicode):
        translated_str = translated_str.decode('utf8')
      # make sure all values in the mapping are unicode
      for k, v in mapping.iteritems():
        if isinstance(v, str):
          v = v.decode('utf8')
        elif isinstance(v, Message):
          v = str(v).decode('utf8')
        unicode_mapping[k] = v
      
      translated_str = Template(translated_str).substitute(unicode_mapping)
    return translated_str

def GlobalTranslationService_translate(self, domain, msgid, *args, **kw):
  context = kw.get('context')
  if context is None:
    # Placeless!
    return msgid

  localizer = getattr(context.getPortalObject(), 'Localizer', None)
  if localizer is None:
    LOG('ERP5Type.patches.Localizer', ERROR, 'could not find a Localizer '
         'object in acquisition context, message will not be translated')
    return msgid
  return localizer.translate(domain, msgid, *args, **kw)

# Apply the monkey patch.
from Products.Localizer.Localizer import Localizer
Localizer.translate = Localizer_translate
Localizer.translate__roles__ = None # public
try:
  from Products.Localizer import GlobalTranslationService
  GlobalTranslationService.translate = GlobalTranslationService_translate
except ImportError:
  pass


# Fix MessageCatalog's manage_export that fails with unicode strings
from Products.Localizer.MessageCatalog import MessageCatalog
original_manage_export = MessageCatalog.manage_export
def cleanup_and_export(self, x, REQUEST=None, RESPONSE=None):
  """Path manage_export to cleanup messages whose keys are unicode objects
  before exporting.
  """
  message_keys = self._messages.keys()
  for k in message_keys:
    if isinstance(k, unicode):
      message = self._messages.get(k.encode('utf8'),
                 self._messages.get(k))
      del self._messages[k]
      self._messages[k.encode('utf8')] = message
  return original_manage_export(self, x, REQUEST=REQUEST, RESPONSE=RESPONSE)
MessageCatalog.manage_export = cleanup_and_export

