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

from Products.CMFCore.utils import getToolByName
from Products.Localizer.MessageCatalog import _marker

class LocalizerTranslationService:
  def translate( self, domain, msgid
               , mapping=None, context=None, target_language=None, default=_marker
               , *args, **kw):
    """
      This translate() method use Localizer and support catalog aliases.
    """
    # This dict define the alias between old Translation Service catalog id
    #   and new Localizer Message Catalog.
    message_catalog_aliases = { "ui"     : "erp5_ui"
                              , "content": "erp5_content"
                              }
    
    # Get Localizer
    localizer = getToolByName(self, 'Localizer')
    # Get the Localizer catalog id
    catalog_id = message_catalog_aliases.get(domain, domain)
    if catalog_id not in localizer.objectIds():
      # No catalog found: return the untranslated string
      return msgid
      
    catalog_obj = localizer[catalog_id]
    # Call the Message Catalog gettext method
    translated_str = catalog_obj.gettext( message = msgid
                                        , lang    = target_language
                                        , default = default
                                        )
    if type(mapping) is type({}):
      return Template(translated_str).substitute(mapping)
    return translated_str


# Use the patched translate() method
from Products.Localizer import GlobalTranslationService, Localizer

GlobalTranslationService.translate = LocalizerTranslationService.translate
Localizer.Localizer.translate = LocalizerTranslationService.translate
Localizer.Localizer.tranlate__roles__ = None # public

