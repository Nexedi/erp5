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
from urllib.parse import urlparse

# Import from itools
from .itools.i18n import get_language_name, get_languages

# Import from Zope
from App.class_init import InitializeClass
from App.Management import Tabs
from AccessControl import ClassSecurityInfo

# Import from Localizer
from .LocalFiles import LocalDTMLFile
from .utils import lang_negotiator, _


class LanguageManager(Tabs):
    """ """

    security = ClassSecurityInfo()

    # TODO For backwards compatibility with Python 2.1 the variable
    # _languages is a tuple.  Change it to a frozenset.
    _languages = ()
    _default_language = None


    ########################################################################
    # API
    ########################################################################
    def get_languages(self):
        """Returns all the object languages.
        """
        return self._languages


    def set_languages(self, languages):
        """Sets the object languages.
        """
        self._languages = tuple(languages)


    def add_language(self, language):
        """Adds a new language.
        """
        if language not in self._languages:
            # Sort the language list, else selected languages
            # can be nearly random.
            new_language_list = tuple(self._languages) + (language,)
            new_language_list = tuple(sorted(new_language_list))
            self._languages = new_language_list

    def del_language(self, language):
        """Removes a language.
        """
        if language in self._languages:
            languages = [ x for x in self._languages if x != language ]
            self._languages = tuple(languages)


    def get_languages_mapping(self):
        """Returns a list of dictionary, one for each objects language. The
        dictionary contains the language code, its name and a boolean value
        that tells wether the language is the default one or not.
        """
        return [ {'code': x,
                  'name': self.get_language_name(x),
                  'default': x == self._default_language}
                 for x in self._languages ]


    def get_available_languages(self, **kw):
        """Returns the langauges available. For example, a language could be
        considered as available only if there is some data associated to it.

        This method is used by the language negotiation code (see
        'get_selected_language'), sometimes you will want to redefine it in
        your classes.
        """
        return self._languages


    def get_default_language(self):
        """Returns the default language.

        This method is used by the language negotiation code (see
        'get_selected_language'), sometimes you will want to redefine it in
        your classes.

        For example, maybe you will want to define it to return always a
        default language, even when internally it is None.
        """
        return self._default_language


    ########################################################################
    # Web API
    ########################################################################

    # Security settings
    security.declarePublic('get_languages')
    security.declareProtected('Manage languages', 'set_languages')
    security.declareProtected('Manage languages', 'add_language')
    security.declareProtected('Manage languages', 'del_language')
    security.declarePublic('get_languages_mapping')


    security.declarePublic('get_language_name')
    def get_language_name(self, id=None):
        """
        Returns the name of the given language code.

        XXX Kept here for backwards compatibility only
        """
        if id is None:
            id = self.get_default_language()
        language_name = get_language_name(id)
        if language_name=='???':
            return self.get_user_defined_language_name(id) or language_name
        else:
            return language_name


    security.declarePublic('get_available_languages')
    security.declarePublic('get_default_language')


    # XXX Kept here temporarily, further refactoring needed
    security.declarePublic('get_selected_language')
    def get_selected_language(self, **kw):
        """
        Returns the selected language. Here the language negotiation takes
        place.

        Accepts keyword arguments which will be passed to
        'get_available_languages'.
        """
        available_languages = self.get_available_languages(*(), **kw)

        return lang_negotiator(available_languages) \
               or self.get_default_language()


    ########################################################################
    # ZMI
    ########################################################################
    manage_options = (
        {'action': 'manage_languages', 'label': u'Languages',
         'help': ('Localizer', 'LM_languages.stx')},)


    def filtered_manage_options(self, REQUEST=None):
        options = Tabs.filtered_manage_options(self, REQUEST=REQUEST)

        # Insert the upgrade form if needed
        if self._needs_upgrade():
            options.insert(0,
                {'action': 'manage_upgradeForm',
                 'label': u'Upgrade',
                 'help': ('Localizer', 'LM_upgrade.stx')})

        # Translate the labels
        r = []
        for option in options:
            option = option.copy()
            option['label'] = _(option['label'])
            r.append(option)

        # Ok
        return r


    security.declareProtected('View management screens', 'manage_languages')
    manage_languages = LocalDTMLFile('ui/LM_languages', globals())


    security.declarePublic('get_all_languages')
    def get_all_languages(self):
        """
        Returns all ISO languages, used by 'manage_languages'.
        """
        return get_languages() + self.get_user_defined_languages()


    security.declareProtected('Manage languages', 'manage_addLanguage')
    def manage_addLanguage(self, language, REQUEST=None, RESPONSE=None):
        """ """
        self.add_language(language)

        if RESPONSE is not None:
            RESPONSE.redirect("%s/manage_languages" % REQUEST['URL1'])


    security.declareProtected('Manage languages', 'manage_delLanguages')
    def manage_delLanguages(self, languages, REQUEST, RESPONSE):
        """ """
        for language in languages:
            self.del_language(language)

        RESPONSE.redirect("%s/manage_languages" % REQUEST['URL1'])


    security.declareProtected('Manage languages', 'manage_changeDefaultLang')
    def manage_changeDefaultLang(self, language, REQUEST=None, RESPONSE=None):
        """ """
        self._default_language = language

        if REQUEST is not None:
            RESPONSE.redirect("%s/manage_languages" % REQUEST['URL1'])


    # Unicode support, custom ZMI
    manage_page_header = LocalDTMLFile('ui/manage_page_header', globals())


    ########################################################################
    # Upgrade
    def _needs_upgrade(self):
        return False


    def _upgrade(self):
        pass


    security.declarePublic('need_upgrade')
    def need_upgrade(self):
        """ """
        return self._needs_upgrade()


    security.declareProtected(
        'Manage Access Rules', 'manage_upgradeForm', 'manage_upgrade')
    manage_upgradeForm = LocalDTMLFile('ui/LM_upgrade', globals())
    def manage_upgrade(self, REQUEST, RESPONSE):
        """ """
        self._upgrade()
        RESPONSE.redirect('manage_main')

    # Add a feature which allows users to be able to add a new language.
    security.declarePublic('get_user_defined_language_name')
    def get_user_defined_language_name(self, id=None):
        """
        Returns the name of the given user defined language code.
        """
        for language_dict in self.get_user_defined_languages():
            if language_dict['code']==id:
                return language_dict['name']

    security.declarePublic('get_user_defined_languages')
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

    def _add_user_defined_language(self, language_name, language_code):
        self.user_defined_languages = (
            getattr(self, 'user_defined_languages', ())+
            ('%s %s' % (language_name, language_code),)
            )
        self._p_changed = True

    def _del_user_defined_language(self, language_code):
        user_defined_languages = []
        for language_dict in self.get_user_defined_languages():
            if language_dict['code']!=language_code:
                user_defined_languages.append('%s %s' %
                                              (language_dict['name'],
                                               language_dict['code']))
        self.user_defined_languages = tuple(user_defined_languages)
        self._p_changed = True



InitializeClass(LanguageManager)
