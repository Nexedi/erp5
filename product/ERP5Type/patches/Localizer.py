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



class LocalizerTranslationService:
  def translate( self, domain, msgid
               , mapping=None, context=None, target_language=None, default=None
               , *args, **kw):
    """
      This translate() method use Localizer and support catalog aliases.
    """

    # This dict define the alias between old Translation Service catalog id
    #   and new Localizer Message Catalog.
    message_catalog_aliases = { "Default": "default"
                              , "ui"     : "erp5_ui"
                              , "content": "erp5_content"
                              , "erp5_ui": "erp5_ui"
                              , "erp5_content": "erp5_content"
                              }

    # Be carefull to not import Localizer anywhere in that Localizer patch:
    #   it can break everything !
    # To update this file in the right way, keep in mind that translate() method
    #   must be able to work outside its LocalizerTranslationService class.
    from Products.Localizer.Localizer import Localizer

    # Get Localizer tool object installed in the ERP5 instance
    if isinstance(self, Localizer):
      # In this case we call the translate method from a script (Base_translateString generally).
      # Exemple of call from a ZODB python script:
      #   context.Localizer.translate('ui', 'Print button')
      # This branch of "if" statement is needed to make the "New Localizer Feature" coded
      #   at the end of the file work.
      localizer = self
    else:
      # This is the normal case
      #   = the one when translation is done via <i18n:translate> tag in Page Template
      localizer = getToolByName(context, 'Localizer', None)
    if localizer == None:
      raise LocalizerPatchError, "Localizer tool not found."

    # Get the Localizer catalog id
    catalog_id = message_catalog_aliases.get(domain, 'default')

    if catalog_id not in localizer.objectIds():
      # No catalog found: return the untranslated string
      return msgid
    catalog_obj = localizer[catalog_id]

    # Adapt Translation Service default value to the Localizer one
    from Products.Localizer.MessageCatalog import _marker
    if default == None: default =_marker

    # Call the Message Catalog gettext method
    translated_str = catalog_obj.gettext( message = msgid
                                        , lang    = target_language
                                        , default = default
                                        )

    # Map the translated string with given parameters
    if type(mapping) is type({}):
      return Template(translated_str).substitute(mapping)
    return translated_str



# Apply the monkey patch.
# Because we don't know when getGlobalTranslationService will be called,
#   we override the setter to force the use of our patched translate() method.
from Products.PageTemplates import GlobalTranslationService
def setGlobalTranslationService(service):
  GlobalTranslationService.translationService = LocalizerTranslationService()
GlobalTranslationService.setGlobalTranslationService = setGlobalTranslationService



### New Localizer Feature ###
# Allow call of translate() in python scripts directly from Localizer object
from Products.Localizer.Localizer import Localizer
Localizer.translate = LocalizerTranslationService.translate
Localizer.tranlate__roles__ = None # public
