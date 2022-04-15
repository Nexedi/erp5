# -*- coding: utf-8 -*-
# Copyright (C) 2000-2004  Juan David Ibáñez Palomar <jdavid@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from __future__ import absolute_import
from urllib.parse import unquote
from contextlib import contextmanager

# Import from Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_parent
from App.class_init import InitializeClass
from OFS.Folder import Folder
from zLOG import LOG, ERROR, INFO, PROBLEM
from zope.interface import implementer
from zope.i18n import translate
from ZPublisher.BeforeTraverse import registerBeforeTraverse, \
     unregisterBeforeTraverse, queryBeforeTraverse, NameCaller

# Import Localizer modules
from .interfaces import ILocalizer
from .LocalFiles import LocalDTMLFile
from .MessageCatalog import MessageCatalog, to_unicode
from .utils import lang_negotiator
from .LanguageManager import LanguageManager



# Constructors
manage_addLocalizerForm = LocalDTMLFile('ui/Localizer_add', globals())
def manage_addLocalizer(self, title, languages, REQUEST=None, RESPONSE=None):
    """
    Add a new Localizer instance.
    """
    self._setObject('Localizer', Localizer(title, languages))

    if REQUEST is not None:
        RESPONSE.redirect('manage_main')


@implementer(ILocalizer)
class Localizer(LanguageManager, Folder):
    """
    The Localizer meta type lets you customize the language negotiation
    policy.
    """

    meta_type = 'Localizer'

    id = 'Localizer'

    _properties = ({'id': 'title', 'type': 'string'},
                   {'id': 'accept_methods', 'type': 'tokens'},
                   {'id': 'user_defined_languages', 'type': 'lines'},)

    accept_methods = ('accept_path', 'accept_cookie', 'accept_url')

    security = ClassSecurityInfo()

    manage_options = \
        (Folder.manage_options[0],) \
        + LanguageManager.manage_options \
        + Folder.manage_options[1:]

    user_defined_languages = ()

    def __init__(self, title, languages):
        self.title = title

        self._languages = languages
        self._default_language = languages[0]


    #######################################################################
    # API / Private
    #######################################################################
    def _getCopy(self, container):
        return Localizer.inheritedAttribute('_getCopy')(self, container)


    def _needs_upgrade(self):
        return not self.hooked()


    def _upgrade(self):
        # Upgrade to 0.9
        if not self.hooked():
            self.manage_hook(1)


    #######################################################################
    # API / Public
    #######################################################################

    # Get some data
    security.declarePublic('get_supported_languages')
    def get_supported_languages(self):
        """
        Get the supported languages, that is the languages that the
        are being working so the site is or will provide to the public.
        """
        return self._languages


    security.declarePublic('get_selected_language')
    def get_selected_language(self):
        """ """
        return lang_negotiator(self._languages) \
               or self._default_language


    # Hooking the traversal machinery
    # Fix this! a new permission needed?
##    security.declareProtected('View management screens', 'manage_hookForm')
##    manage_hookForm = LocalDTMLFile('ui/Localizer_hook', globals())
##    security.declareProtected('Manage properties', 'manage_hook')
    security.declarePrivate('manage_hook')
    def manage_hook(self, hook=0):
        """ """
        if hook != self.hooked():
            if hook:
                hook = NameCaller(self.id)
                registerBeforeTraverse(aq_parent(self), hook, self.meta_type)
            else:
                unregisterBeforeTraverse(aq_parent(self), self.meta_type)


    security.declarePublic('hooked')
    def hooked(self):
        """ """
        if queryBeforeTraverse(aq_parent(self), self.meta_type):
            return 1
        return 0


    # New code to control the language policy
    security.declarePrivate('accept_cookie')
    def accept_cookie(self, accept_language):
        """Add the language from a cookie."""
        lang = self.REQUEST.cookies.get('LOCALIZER_LANGUAGE', None)
        if lang is not None:
            accept_language.set(lang, 2.0)


    security.declarePrivate('accept_path')
    def accept_path(self, accept_language):
        """Add the language from the path."""
        stack = self.REQUEST['TraversalRequestNameStack']
        if stack and (stack[-1] in self._languages):
            lang = stack.pop()
            accept_language.set(lang, 3.0)


    security.declarePrivate('accept_url')
    def accept_url(self, accept_language):
        """Add the language from the URL."""
        lang = self.REQUEST.form.get('LOCALIZER_LANGUAGE')
        if lang is not None:
            accept_language.set(lang, 2.0)


    def __call__(self, container, REQUEST):
        """Hooks the traversal path."""
        try:
            accept_language = REQUEST['AcceptLanguage']
        except KeyError:
            return

        for id in self.accept_methods:
            try:
                method = getattr(self, id)
                method(accept_language)
            except:
                LOG(self.meta_type, PROBLEM,
                    'method "%s" raised an exception.' % id, error=True)


    # Changing the language, useful snippets
    security.declarePublic('get_languages_map')
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


    security.declarePublic('changeLanguage')
    changeLanguageForm = LocalDTMLFile('ui/changeLanguageForm', globals())
    def changeLanguage(self, lang, goto=None, expires=None):
        """Change the user language to `lang`.

        This method will set a cookie and redirect to `goto` URL.
        """
        request = self.REQUEST
        response = request.RESPONSE

        # Changes the cookie (it could be something different)
        parent = aq_parent(self)
        path = parent.absolute_url()[len(request['SERVER_URL']):] or '/'
        if expires is None:
            response.setCookie('LOCALIZER_LANGUAGE', lang, path=path)
        else:
            response.setCookie('LOCALIZER_LANGUAGE', lang, path=path,
                               expires=unquote(expires))
        # Comes back
        if goto is None:
            goto = request['HTTP_REFERER']

        response.redirect(goto)

    security.declarePublic('translationContext')
    @contextmanager
    def translationContext(self, lang):
      """Context manager to temporarily change the current language.
      """
      class ForcedLanguage:
        __allow_access_to_unprotected_subobjects__ = 1
        def __init__(self, lang):
          self.lang = lang
        def select_language(self, available_languages):
          return self.lang
        def set(self, lang, priority):
          if lang != self.lang:
            LOG('Localizer', PROBLEM,
               'Cannot change language inside a translationContext', error=True)
      MARKER = []
      from .patches import get_request # late import, as this is patched by
                                      # unit tests
      request = get_request() # Localizer always use this request internally
      old_accept_language = request.get('AcceptLanguage', MARKER)
      request.set('AcceptLanguage', ForcedLanguage(lang))
      try:
        assert self.get_selected_language() == lang
        yield
      finally:
        request.other.pop('AcceptLanguage')
        if old_accept_language is not MARKER:
          request.set('AcceptLanguage', old_accept_language)

    security.declarePublic('translate')
    def translate(self, domain, msgid, lang=None, *args, **kw):
        """
        backward compatibility shim over zope.i18n.translate. Please avoid.
        """
        # parameter reordering/mangling necessary
        assert not args
        if lang is not None:
            kw['target_language'] = lang
        return translate(to_unicode(msgid), domain=domain, **kw)

InitializeClass(Localizer)


# Hook/unhook the traversal machinery
# Support for copy, cut and paste operations

def Localizer_moved(object, event):
    container = event.oldParent
    if container is not None:
        unregisterBeforeTraverse(container, object.meta_type)

    container = event.newParent
    if container is not None:
        id = object.id
        container = container.this()
        hook = NameCaller(id)
        registerBeforeTraverse(container, hook, object.meta_type)
