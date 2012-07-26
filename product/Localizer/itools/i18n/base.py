# -*- coding: utf-8 -*-
# Copyright (C) 2002-2003, 2007-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
from ..utils import get_abspath


# Initializes a dictionary containing the iso 639 language codes/names
languages = {}
filename = get_abspath('languages.txt')
for line in open(filename).readlines():
    line = line.strip()
    if line and line[0] != '#':
        code, name = line.split(' ', 1)
        languages[code] = name

# Builds a sorted list with the languages code and name
language_codes = languages.keys()
language_codes.sort()
langs = [ {'code': x, 'name': languages[x]} for x in language_codes ]



def has_language(code):
    return code in languages



def get_languages():
    """Returns a list of tuples with the code and the name of each language.
    """
    return [ x.copy() for x in langs ]



def get_language_name(code):
    """Returns the name of a language.
    """
    # FIXME The value returned should be a MSG object, but the MSG class comes
    # from the itools.gettext module, which is higher level than itools.i18n
    if code in languages:
        return languages[code]
    return u'???'

