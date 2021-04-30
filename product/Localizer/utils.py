# -*- coding: utf-8 -*-
# Copyright (C) 2000-2003  Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from itools
from __future__ import absolute_import
from .itools.utils import get_abspath
from .itools.i18n import AcceptLanguageType, init_language_selector

# Import from Zope
from App.Common import package_home

# Import from Localizer
from .patches import get_request


# Package home
ph = package_home(globals())

# Initializes a list with the charsets
charsets = [ x.strip() for x in open(ph + '/charsets.txt').readlines() ]



###########################################################################
# Language negotiation
###########################################################################
def lang_negotiator(available_languages):
    """Receives two ordered lists, the list of user preferred languages and
    the list of available languages. Returns the first user pref.  language
    that is available, if none is available returns None.
    """
    request = get_request()
    if request is None:
        return None

    try:
        accept = request['AcceptLanguage']
    except KeyError:
        return None

    return accept.select_language(available_languages)


init_language_selector(lang_negotiator)


###########################################################################
# Provide an API to access translations stored as MO files in the 'locale'
# directory.
###########################################################################
class DomainAware(object):
    """
    This class is just a stub. We're not interested in filesystem-based
    po-file translations.

    All subclasses should be either changed not to require DomainAware
    or removed altogether.
    """

    def __init__(self, namespace):
        mname = namespace['__name__']
        domain = get_abspath('locale', mname=mname)
        self.class_domain = domain


    def gettext(self, message, language=None):
        return message

_ = DomainAware(globals()).gettext


###########################################################################
# Defines strings that must be internationalized
###########################################################################

# Tabs of the management screens
u'Contents'
u'View'
u'Properties'
u'Security'
u'Undo'
u'Ownership'
u'Find'
# Languages (FIXME This will be removed once we upgrade to itools 0.60)
u'Abkhazian'
u'Afar'
u'Afrikaans'
u'Albanian'
u'Amharic'
u'Arabic'
u'Armenian'
u'Assamese'
u'Aymara'
u'Azerbaijani'
u'Bashkir'
u'Basque'
u'Bengali'
u'Bhutani'
u'Bihari'
u'Bislama'
u'Bosnian'
u'Breton'
u'Bulgarian'
u'Burmese'
u'Belarusian'
u'Cambodian'
u'Catalan'
u'Chinese'
u'Chinese/China'
u'Chinese/Taiwan'
u'Cornish'
u'Corsican'
u'Croatian'
u'Czech'
u'Danish'
u'Dutch'
u'Dutch/Belgium'
u'English'
u'English/United Kingdom'
u'English/United States'
u'Esperanto'
u'Estonian'
u'Faroese'
u'Fiji'
u'Finnish'
u'French'
u'French/Belgium'
u'French/Canada'
u'French/France'
u'French/Switzerland'
u'Frisian'
u'Galician'
u'Georgian'
u'German'
u'German/Austria'
u'German/Germany'
u'German/Switzerland'
u'Greek'
u'Greenlandic'
u'Guarani'
u'Gujarati'
u'Hausa'
u'Hebrew'
u'Hindi'
u'Hungarian'
u'Icelandic'
u'Indonesian'
u'Interlingua'
u'Interlingue'
u'Inuktitut'
u'Inupiak'
u'Irish'
u'Italian'
u'Japanese'
u'Javanese'
u'Kannada'
u'Kashmiri'
u'Kazakh'
u'Kinyarwanda'
u'Kirghiz'
u'Kirundi'
u'Korean'
u'Kurdish'
u'Laothian'
u'Latin'
u'Latvian'
u'Lingala'
u'Lithuanian'
u'Luxembourgish'
u'Macedonian'
u'Malagasy'
u'Malay'
u'Malayalam'
u'Maltese'
u'Maori'
u'Marathi'
u'Moldavian'
u'Mongolian'
u'Nauru'
u'Nepali'
u'Northern Saami'
u'Norwegian'
u'Occitan'
u'Oriya'
u'Oromo'
u'Pashto'
u'Persian'
u'Polish'
u'Portuguese'
u'Portuguese/Brazil'
u'Punjabi'
u'Quechua'
u'Rhaeto-Romance'
u'Romanian'
u'Russian'
u'Samoan'
u'Sangho'
u'Sanskrit'
u'Scots Gaelic'
u'Serbian'
u'Serbo-Croatian'
u'Sesotho'
u'Setswana'
u'Shona'
u'Sindhi'
u'Sinhalese'
u'Siswati'
u'Slovak'
u'Slovenian'
u'Somali'
u'Spanish'
u'Spanish/Argentina'
u'Spanish/Colombia'
u'Spanish/Mexico'
u'Spanish/Spain'
u'Sundanese'
u'Swahili'
u'Swedish'
u'Tagalog'
u'Tajik'
u'Tamil'
u'Tatar'
u'Telugu'
u'Thai'
u'Tibetan'
u'Tigrinya'
u'Tonga'
u'Tsonga'
u'Turkish'
u'Turkmen'
u'Twi'
u'Uighur'
u'Ukrainian'
u'Urdu'
u'Uzbek'
u'Vietnamese'
u'Volapuk'
u'Welsh'
u'Wolof'
u'Xhosa'
u'Yiddish'
u'Yoruba'
u'Zhuang'
u'Zulu'
