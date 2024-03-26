# -*- coding: utf-8 -*-
# Copyright (C) 2000-2005  Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
import os.path

# Import from Zope
from App.ImageFile import ImageFile
from DocumentTemplate.DT_String import String

# Import from Localizer
from . import patches as _
from . import Localizer, MessageCatalog
from .LocalFiles import LocalDTMLFile


misc_ = {'arrow_left': ImageFile('img/arrow_left.gif', globals()),
         'arrow_right': ImageFile('img/arrow_right.gif', globals()),
         'eye_opened': ImageFile('img/eye_opened.gif', globals()),
         'eye_closed': ImageFile('img/eye_closed.gif', globals()),
         'obsolete': ImageFile('img/obsolete.gif', globals())}


def initialize(context):
    # Check Localizer is not installed with a name different than Localizer
    # (this is a common mistake).
    filename = os.path.split(os.path.split(__file__)[0])[1]
    if filename != 'Localizer':
        raise RuntimeError(
            "The Localizer product must be installed within the 'Products'"
            " folder with the name 'Localizer' (not '%s')." % filename
        )

    # XXX This code has been written by Cornel Nitu, it may be a solution to
    # upgrade instances.
##    root = context._ProductContext__app
##    for item in root.PrincipiaFind(root, obj_metatypes=['LocalContent'],
##                                   search_sub=1):
##        item[1].manage_upgrade()

    # Register the Localizer
    context.registerClass(Localizer.Localizer,
                          constructors = (Localizer.manage_addLocalizerForm,
                                          Localizer.manage_addLocalizer),
                          icon = 'img/localizer.gif')

    # Register MessageCatalog
    context.registerClass(
        MessageCatalog.MessageCatalog,
        constructors = (MessageCatalog.manage_addMessageCatalogForm,
                        MessageCatalog.manage_addMessageCatalog),
        icon='img/message_catalog.gif')
