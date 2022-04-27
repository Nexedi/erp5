# -*- coding: UTF-8 -*-
# Copyright (C) 2004, 2006-2009 J. David Ibáñez <jdavid.ibp@gmail.com>
# Copyright (C) 2008 Henry Obein <henry.obein@gmail.com>
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

# Import from itools
from accept import AcceptLanguageType, get_accept, select_language
from accept import init_language_selector
from fuzzy import get_distance, get_similarity, is_similar, get_most_similar
from languages import has_language, get_languages, get_language_name
from locale_ import format_date, format_time, format_datetime
from locale_ import format_number
from oracle import guess_language, is_asian_character, is_punctuation



__all__ = [
    # accept
    'AcceptLanguageType',
    'get_accept',
    'select_language',
    'init_language_selector',
    # fuzzy
    'get_distance',
    'get_similarity',
    'is_similar',
    'get_most_similar',
    # locale
    'format_date',
    'format_time',
    'format_datetime',
    'format_number',
    # oracle
    'guess_language',
    'is_asian_character',
    'is_punctuation',
    # languages
    'has_language',
    'get_languages',
    'get_language_name',
    ]

