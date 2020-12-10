# -*- coding: UTF-8 -*-
# Copyright (C) 2002-2008, 2010 J. David Ibáñez <jdavid.ibp@gmail.com>
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

"""
This module implements the Accept-Language request header of the HTTP
protocol.
"""

# Import from the Standard Library
import __builtin__
from decimal import Decimal
from locale import getdefaultlocale



zero = Decimal('0.0')
one = Decimal('1.0')



# FIXME This class belongs to the public API, but it is not exposed since
# we never create it directly (we use AcceptLanguageType).
class AcceptLanguage(dict):
    """Implements the Accept-Language tree.
    """

    def set(self, key, quality):
        if not isinstance(quality, Decimal):
            if not isinstance(quality, str):
                quality = str(quality)
            quality = Decimal(quality)

        if key == '*':
            key = ''
        self[key] = quality


    def get_quality(self, language):
        """This method returns the quality of the given language. As defined
        by the RFC 2616, if a langage is not defined it inherits the quality
        from a "parent" language; for instance, if 'fr-FR' is not defined but
        'fr' is, then 'fr-FR' inherits the quality from 'fr'.

        To make the difference between an exact match and an inherited value,
        this method returns a tuple: first value is the quality, and second
        value is the number of steps it had to go back in the inheritance
        chain (0 for an exact match).
        """
        steps = 0
        while language and language not in self:
            language = '-'.join(language.split('-')[:-1])
            steps += 1

        return self.get(language, zero), steps


    def select_language(self, languages):
        """This is the selection language algorithm, it returns the user
        prefered language for the given list of available languages, if the
        intersection is void returns None.

        The criterias used to select a language are:

        1. The quality
        2. The distance to the exact match
        3. The order in the 'languages' parameter
        """
        language, quality, steps = None, zero, 100
        for lang in languages:
            q, s = self.get_quality(lang)
            if q > quality or (q and q == quality and s < steps):
                language, quality, steps = lang, q, s

        return language



class AcceptLanguageType(object):

    @staticmethod
    def decode(data):
        """From a string formatted as specified in the RFC2616, it builds a
        data structure which provides a high level interface to implement
        language negotiation.
        """
        data = data.strip()
        if not data:
            return AcceptLanguage({})

        accept = {}
        for language in data.lower().split(','):
            language = language.strip()
            if ';' in language:
                language, quality = language.split(';')
                # Get the number (remove "q=")
                quality = Decimal(quality.strip()[2:])
            else:
                quality = one

            if language == '*':
                language = ''

            accept[language] = quality

        return AcceptLanguage(accept)


    @staticmethod
    def encode(accept):
        # Sort
        accept = [ (y, x) for x, y in accept.items() ]
        accept.sort()
        accept.reverse()
        # Encode
        data = []
        for quality, language in accept:
            if language == '':
                if quality == zero:
                    continue
                language = '*'
            if quality == one:
                data.append(language)
            else:
                data.append('%s;q=%s' % (language, quality))
        return ', '.join(data)



def get_accept():
    language = getdefaultlocale()[0]
    if language is None:
        language = ''
    elif '_' in language:
        language = language.replace('_', '-')
        language = '%s, %s;q=0.5' % (language, language.split('-')[0])

    return AcceptLanguageType.decode(language)



def select_language(languages=None):
    return get_accept().select_language(languages)



def init_language_selector(language_selector=select_language):
    __builtin__.__dict__['select_language'] = language_selector


# Set default language selector
init_language_selector(select_language)


