# -*- coding: UTF-8 -*-
# Copyright (C) 2000-2002  Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# Import from Zope
from ExtensionClass import Base


class LocalAttribute(Base):
    """
    Provides a way to override class variables, useful for example
    for title (defined in SimpleItem).
    """

    def __init__(self, id):
        self.id = id

    def __of__(self, parent):
        return parent.getLocalAttribute(self.id)


class LocalAttributesBase:
    def getLocalAttribute(self, name, lang=None):
        """ """
        raise NotImplemented


class LocalAttributes(LocalAttributesBase):
    """
    Example of a 'LocalAttributesBase' derived class, this also a base class
    for 'LocalFolder.LocalFolder' and 'Locale.Locale', it can be considered
    the default implementation.

    Returns attributes of the form <name>_<lang>. When <lang> has more than
    one level, for example es-CO, the dashes are transformed to underscores,
    as dashes aren't valid charecters for identifiers in Python. For example,
    the call 'getLocalAttribute("long_date", "es-CO")' would return
    'self.long_date_es_CO'.
    """

    def getLocalAttribute(self, name, lang=None):
        if lang is None:
            lang = self.get_selected_language()

        lang = lang.replace('-', '_')
        name = '%s_%s' % (name, lang)

        return getattr(self, name)
