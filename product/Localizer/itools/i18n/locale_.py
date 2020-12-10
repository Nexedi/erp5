# -*- coding: UTF-8 -*-
# Copyright (C) 2007, 2009 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2010 Hervé Cauwelier <herve@oursours.net>
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

# Import from the Standard Library
from decimal import Decimal

# Import from itools
from accept import get_accept


def get_format(source, accept):
    # By default use the computer's locale
    if accept is None:
        accept = get_accept()

    # Negotiate
    available_languages = source.keys()
    language = accept.select_language(available_languages)
    if language is None:
        language = 'en'

    # The format
    return source[language]



#
# Date and Time
#

def format_date(x, accept=None):
    format = get_format(date_formats, accept)[0]
    return x.strftime(format)


def format_time(x, accept=None):
    format = get_format(date_formats, accept)[1]
    return x.strftime(format)


def format_datetime(x, accept=None):
    format = get_format(date_formats, accept)[2]
    return x.strftime(format)



#
# Decimal
#

# http://docs.python.org/library/decimal.html#recipes
# Modified for unicode and trailing currency
def moneyfmt(value, places=2, curr=u'', sep=u',', dp=u'.', pos=u'',
        neg=u'-', trailneg=u''):
    """Convert Decimal to a money formatted unicode.

    places:  required number of places after the decimal point
    curr:    optional currency symbol (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-1,234,567.89$'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '(1,234,567.89$)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(unicode, digits)
    build, next = result.append, digits.pop
    if curr:
        build(curr)
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else u'0')
    build(dp)
    if not digits:
        build(u'0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(neg if sign else pos)
    return u''.join(reversed(result))


def format_number(x, places=2, curr='', pos=u'', neg=u'-', trailneg=u"",
                  accept=None):
    """Convert Decimal to a number formatted unicode.

    places:  required number of places after the decimal point
    curr:    optional currency symbol (may be blank)
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank
    """
    if type(x) is not Decimal:
        x = Decimal(x)
    format = get_format(number_formats, accept)
    return moneyfmt(x, places=places, curr=curr, pos=pos, neg=neg,
            trailneg=trailneg, **format)



###########################################################################
# Initialize the module
###########################################################################

date_formats = {
    # Date, Time, DateTime
    'en': ('%d/%m/%Y', '%H:%M', '%d/%m/%Y %H:%M'),
    'es': ('%d/%m/%Y', '%H.%M', '%d/%m/%Y %H.%M'),
    'fr': ('%d/%m/%Y', '%Hh%M', '%d/%m/%Y %Hh%M'),
    }


number_formats = {
    # See "moneyfmt" docstring for help
    'en': {'sep': u',', 'dp': u'.'},
    'es': {'sep': u'.', 'dp': u','},
    'fr': {'sep': u' ', 'dp': u','},
    }
