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

from Products.CMFCore.utils import getToolByName

# Template() is a new method of python 2.4, that's why we have the string.py
#   file in patches directory.
try:
  from string import Template
except ImportError:
  from Products.ERP5Type.patches.string import Template


from zLOG import LOG

class LocalizerPatchError(Exception):
  """Error wen trying to use or apply the Localizer patch"""

# This patch will not work if Translation Service Zope product exist on the system
try:
  from Products import TranslationService
  LOG("LocalizerPatchError", 100,"Translation Service Zope Product (%s) and Translation Service tools must be deleted to let Localizer Patch work." % (repr(TranslationService)))
except ImportError:
  pass


def Localizer_translate(self, domain, msgid, mapping=None, *args, **kw):
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
    if catalog_id not in self.objectIds():
      # No catalog found: use the default one
      catalog_id = 'default'
    catalog_obj = self[catalog_id]

    # Call the Message Catalog gettext method
    params = {}
    for key in ('lang', 'add', 'default'):
      if key in kw:
        params[key] = kw[key]
    if 'target_language' in kw:
      params['lang'] = kw['target_language']
    translated_str = catalog_obj.gettext(msgid, **params)

    # Map the translated string with given parameters
    if type(mapping) is type({}):
      return Template(translated_str).substitute(mapping)
    return translated_str

def GlobalTranslationService_translate(self, domain, msgid, *args, **kw):
  context = kw.get('context')
  if context is None:
    # Placeless!
    return msgid

  return context.Localizer.translate(domain, msgid, *args, **kw)

# Apply the monkey patch.
try:
  from Products.Localizer import GlobalTranslationService
  from Products.Localizer.Localizer import Localizer
  GlobalTranslationService.translate = GlobalTranslationService_translate
  Localizer.translate = Localizer_translate
  Localizer.translate__roles__ = None # public
except ImportError:
  pass
