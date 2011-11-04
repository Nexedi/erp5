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

from string import Template
from itools import i18n
from Products.ERP5Type.Message import Message
from zLOG import LOG, ERROR

# This patch will not work if Translation Service Zope product exist on the system
try:
  from Products import TranslationService
  LOG("ERP5Type.patches.Localizer", ERROR, "Translation Service Zope Product"
      " (%s) and Translation Service tools must be deleted to let Localizer "
      "Patch work." % (repr(TranslationService)))
except ImportError:
  pass

# This dict define the alias between old Translation Service catalog id
#   and new Localizer Message Catalog.
message_catalog_aliases = { "Default": "default"
                          , "ui"     : "erp5_ui"
                          , "content": "erp5_content"
                          }

# "invert" message_catalog_aliases mapping
message_catalog_alias_sources = {}
for name, value in message_catalog_aliases.items():
  message_catalog_alias_sources.setdefault(value, []).append(name)

# BACK: This method is not used in Zope 2.12. Drop when we drop support for
# Zope 2.8
def Localizer_translate(self, domain, msgid, lang=None, mapping=None, *args, **kw):
    """
      This translate() method use Localizer and support catalog aliases.
    """
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

# Apply the monkey patch.
from Products.Localizer.Localizer import Localizer
Localizer.translate = Localizer_translate
Localizer.translate__roles__ = None # public

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


# Add a feature which allows users to be able to add a new language.
#
# Patch to LanguageManager.py
#
def get_languages_mapping(self):
    """
    Returns a list of dictionary, one for each objects language. The
    dictionary contains the language code, its name and a boolean
    value that tells wether the language is the default one or not.
    """
    return [ {'code': x,
              'name': self.get_language_name(x),
              'default': x == self._default_language}
             for x in self._languages ]

def get_language_name(self, id=None):
    """
    Returns the name of the given language code.

    XXX Kept here for backwards compatibility only
    """
    if id is None:
        id = self.get_default_language()
    language_name = i18n.get_language_name(id)
    if language_name=='???':
        return self.get_user_defined_language_name(id) or language_name
    else:
        return language_name

# New method
def get_user_defined_language_name(self, id=None):
    """
    Returns the name of the given user defined language code.
    """
    for language_dict in self.get_user_defined_languages():
        if language_dict['code']==id:
            return language_dict['name']

def get_all_languages(self):
    """
    Returns all ISO languages, used by 'manage_languages'.
    """
    return i18n.get_languages() + self.get_user_defined_languages()

# New method
def get_user_defined_languages(self):
    user_define_language_dict_list = []
    localizer = getattr(self, 'Localizer', None)
    if localizer is not None:
        for value in getattr(self, 'user_defined_languages', ()):
            splitted_value = value.split(' ', 1)
            if len(splitted_value)==2:
                user_define_language_dict_list.append(
                    {'name':splitted_value[0].strip(),
                     'code':splitted_value[1].strip(),})
    return user_define_language_dict_list

# New method
def _add_user_defined_language(self, language_name, language_code):
    self.user_defined_languages = (
        getattr(self, 'user_defined_languages', ())+
        ('%s %s' % (language_name, language_code),)
        )
    self._p_changed = True

# New method
def _del_user_defined_language(self, language_code):
    user_defined_languages = []
    for language_dict in self.get_user_defined_languages():
        if language_dict['code']!=language_code:
            user_defined_languages.append('%s %s' %
                                          (language_dict['name'],
                                           language_dict['code']))
    self.user_defined_languages = tuple(user_defined_languages)
    self._p_changed = True

# Override add_language so that languages are always sorted.
# Otherwise, selected languages can be nearly random.
def add_language(self, language):
    """
    Adds a new language.
    """
    if language not in self._languages:
        new_language_list = tuple(self._languages) + (language,)
        new_language_list = tuple(sorted(new_language_list))
        self._languages = new_language_list

from Products.Localizer import LanguageManager
LanguageManager.LanguageManager.get_languages_mapping = get_languages_mapping
LanguageManager.LanguageManager.get_language_name = get_language_name
LanguageManager.LanguageManager.get_all_languages = get_all_languages
LanguageManager.LanguageManager.get_user_defined_language_name = get_user_defined_language_name
LanguageManager.LanguageManager.get_user_defined_languages = get_user_defined_languages
LanguageManager.LanguageManager._add_user_defined_language = _add_user_defined_language
LanguageManager.LanguageManager._del_user_defined_language = _del_user_defined_language
LanguageManager.LanguageManager.add_language = add_language
LanguageManager.InitializeClass(LanguageManager.LanguageManager)

#
# Patch to Localizer.py
#
_properties = ({'id': 'title', 'type': 'string'},
               {'id': 'accept_methods', 'type': 'tokens'},
               {'id': 'user_defined_languages', 'type': 'lines'},)

user_defined_languages = ()

def get_languages_map(self):
    """
    Return a list of dictionaries, each dictionary has the language
    id, its title and a boolean value to indicate wether it's the
    user preferred language, for example:
       [{'id': 'en', 'title': 'English', 'selected': 1}]
     Used in changeLanguageForm.
    """
    # For now only LPM instances are considered to be containers of
    # multilingual data.
    try:
        ob = self.getLocalPropertyManager()
    except AttributeError:
        ob = self

    ob_language = ob.get_selected_language()
    ob_languages = ob.get_available_languages()

    langs = []
    for x in ob_languages:
        langs.append({'id': x, 'title': self.get_language_name(x),
                      'selected': x == ob_language})
    return langs

from Products.Localizer import Localizer
Localizer.Localizer._properties = _properties
Localizer.Localizer.user_defined_languages = user_defined_languages
Localizer.Localizer.get_languages_map = get_languages_map
Localizer.InitializeClass(Localizer.Localizer)

# BACK: Can't write a configure.zcml that works on both Zope 2.8 and Zope 2.12
# So we monkeypatch the subscriber instead. When we drop support for Zope 2.8
# write a proper subscriber for MessageCatalog and IObjectMovedEvent
if 1:
  from Products.Localizer.MessageCatalog import (MessageCatalog_moved as
                                                 MessageCatalog_moved_orig)
  from zope.component import getSiteManager
  from zope.i18n.interfaces import ITranslationDomain
  import Products.Localizer.MessageCatalog
  def MessageCatalog_moved(object, event):
    """
    Install ITranslationDomain aliases alongside the original
    MessageCatalog names
    """
    MessageCatalog_moved_orig(object, event)
    if event.oldParent is not None:
      # unregister old aliases
      oldAliases = message_catalog_alias_sources.get(event.oldName, ())
      sm = getSiteManager(event.oldParent)
      for alias in oldAliases:
        sm.unregisterUtility(object, ITranslationDomain, alias)

    if event.newParent is not None:
      # register new aliases
      newAliases = message_catalog_alias_sources.get(event.newName, ())
      sm = getSiteManager(event.newParent)
      # FIXME: install aliases only if inside an ERP5Site
      # but how to do that without causing circular dependencies? ERP5Site
      # needs to implement an IERP5Site interface, declared inside
      # Products.ERP5Type.interfaces
      for alias in newAliases:
        sm.registerUtility(object, ITranslationDomain, alias)
  
  Products.Localizer.MessageCatalog.MessageCatalog_moved = MessageCatalog_moved
