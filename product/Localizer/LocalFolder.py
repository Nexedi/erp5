# -*- coding: UTF-8 -*-
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

# Import from Zope
from App.Common import package_home
from OFS.Folder import Folder

# Import from Localizer
from LanguageManager import LanguageManager
from LocalFiles import LocalDTMLFile
from LocalAttributes import LocalAttribute, LocalAttributes
from utils import _



manage_addLocalFolderForm = LocalDTMLFile('ui/LocalFolder_add', globals())
def manage_addLocalFolder(self, id, title, languages, REQUEST=None):
    """ """
    id = id.strip()
    self._setObject(id, LocalFolder(id, title, languages))

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)



class LocalFolder(LanguageManager, LocalAttributes, Folder):
    """ """

    meta_type = 'LocalFolder'

    _properties = ({'id': 'title', 'type': 'string'},)


    def __init__(self, id, title, languages):
        self.id = id
        self.title = title

        # Language Manager data
        self._languages = tuple(languages)
        self._default_language = languages[0]

        # Local attributes
        self._local_attributes = ()


    manage_options = \
        Folder.manage_options[:1] \
        + ({'action': 'manage_attributes', 'label': u'Attributes'},) \
        + LanguageManager.manage_options \
        + Folder.manage_options[1:]


    # Manage attributes
    manage_attributes = LocalDTMLFile('ui/LocalFolder_attributes', globals())

    def get_local_attributes(self):
        return self._local_attributes


    def manage_delAttributes(self, attributes, REQUEST=None, RESPONSE=None):
        """ """
        local_attributes = list(self._local_attributes)

        for attr in attributes:
            local_attributes.remove(attr)
            delattr(self, attr)

        self._local_attributes = tuple(local_attributes)

        if RESPONSE is not None:
            RESPONSE.redirect("%s/manage_attributes" % REQUEST['URL1'])


    def manage_addAttribute(self, id, REQUEST=None, RESPONSE=None):
        """ """
        id = id.strip()
        setattr(self, id, LocalAttribute(id))

        self._local_attributes = self._local_attributes + (id,)

        if RESPONSE is not None:
            RESPONSE.redirect("%s/manage_attributes" % REQUEST['URL1'])
