# -*- coding: UTF-8 -*-
# Copyright (C) 2004 Thierry Fromon <from.t@free.fr>
# Copyright (C) 2006-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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


def get_distance(a, b):
    """
    This function was giving by Magnus Lie Hetland. It calculates the gap
    (mathematical distance) between two strings with the cost of word's
    translation inside the string.
    """
    # XXX Find URL to original code, check license
    c = {}
    n = len(a)
    m = len(b)
    for i in range(0, n+1):
        c[i, 0] = i
    for j in range(0, m+1):
        c[0, j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            x = c[i-1, j] + 1
            y = c[i, j-1] + 1
            if a[i-1] == b[j-1]:
                z = c[i-1, j-1]
            else:
                z = c[i-1, j-1] + 1
            c[i, j] = min(x, y, z)
    return c[n, m]


def get_similarity(a, b):
    """
    Return a gap and a percent that takes account of abrevations.
    """
    length = max(len(a), len(b))
    distance = get_distance(a, b)
    return 1 - (float(distance) / float(length))


def is_similar(a, b, limit=0.8):
    """
    Returns True if both text strings are close enough, False otherwise.
    The optional parameter 'limit' defines the degree of similarity required
    to be considered 'close enough', it is a float value between '0'
    (completely different) and '1' (the same string).
    """
    return get_similarity(a, b) >= limit


def get_most_similar(a, *args):
    """
    Returns the text string from 'args' that is closest to the given string.
    """
    if not args:
        return None

    options = [ (get_similarity(a, x), x) for x in args ]
    options.sort()
    return options[-1][1]


##############################################################################
# XXX To enable this feature a deep work on abbreviations must be done
##dictionary = {u'Monsieur': (u'Mr', u'M', u'M.', u'Mr.'),
##              u'Madame': (u'Md', u'Md.')}

##punctuations = [u'.', u',', u';', u'?', '!', u"'", u'"', u'¡', u'¿']


##def expand_abbreviations(text):
##    """
##    Return a text without abrevation.
##    """
##    t = ' ' + text + ' '
##    for i in punctuations:
##        t = t.replace(i, ' ' + i + ' ')
##    for word, abrevations in dictionary.items():
##        for abrevation in abrevations:
##            t = t.replace(' ' + abrevation + ' ', ' ' + word + ' ')
##    return t


##def get_distance(a, b):
##    """
##    Return a gap and a percent that takes account of abrevations.
##    """
##    a_expanded = expand_abbreviations(a)
##    b_expanded = expand_abbreviations(b)
##    length = max(len(a), len(b))
##    length_expanded = 5 * max(len(a_expanded), len(b_expanded))
##    gap = get_gap(a, b)
##    gap_expanded = 5 * get_gap(a_expanded, b_expanded)
##    percent = 100 - 100 * (gap_expanded + gap) / (length_expanded + length)
##    return gap, percent
