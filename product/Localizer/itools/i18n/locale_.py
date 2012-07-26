# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
Output dates and times in locale format.
"""

# Import from itools
from accept import get_accept


formats = {
    # Date, Time, DateTime
    'en': ('%d/%m/%Y', '%H:%M', '%d/%m/%Y %H:%M'),
    'es': ('%d/%m/%Y', '%H.%M', '%d/%m/%Y %H.%M'),
    'fr': ('%d/%m/%Y', '%Hh%M', '%d/%m/%Y %Hh%M'),
    }



available_languages = formats.keys()



def get_format(accept):
    # By default use the computer's locale
    if accept is None:
        accept = get_accept()

    # Negotiate
    language = accept.select_language(available_languages)
    if language is None:
        language = 'en'

    # The format
    return formats[language]


def format_date(x, accept=None):
    format = get_format(accept)[0]
    return x.strftime(format)


def format_time(x, accept=None):
    format = get_format(accept)[1]
    return x.strftime(format)


def format_datetime(x, accept=None):
    format = get_format(accept)[2]
    return x.strftime(format)

