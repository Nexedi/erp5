# -*- coding: UTF-8 -*-
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

# Check whether itools is installed
msg = ('itools 0.50 or later is needed, download from '
       'http://download.hforge.org/itools/0.50')
try:
    import itools
except ImportError:
    raise ImportError, msg
# Check itools is version 0.50 or later
if itools.__version__ < '0.50':
    raise ImportError, msg

# Import from the Standard Library
import os.path

# Import from Zope
from App.ImageFile import ImageFile
from DocumentTemplate.DT_String import String

# Import from Localizer
from patches import get_request
import Localizer, LocalContent, MessageCatalog, LocalFolder
from LocalAttributes import LocalAttribute
from LocalFiles import LocalDTMLFile, LocalPageTemplateFile
from LocalPropertyManager import LocalPropertyManager, LocalProperty
from GettextTag import GettextTag



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
        message = (
            "The Localizer product must be installed within the 'Products'"
            " folder with the name 'Localizer' (not '%s').") % filename
        raise RuntimeError, message

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

    # Register LocalContent
    context.registerClass(
        LocalContent.LocalContent,
        constructors = (LocalContent.manage_addLocalContentForm,
                        LocalContent.manage_addLocalContent),
        icon='img/local_content.gif')

    # Register MessageCatalog
    context.registerClass(
        MessageCatalog.MessageCatalog,
        constructors = (MessageCatalog.manage_addMessageCatalogForm,
                        MessageCatalog.manage_addMessageCatalog),
        icon='img/message_catalog.gif')

    # Register LocalFolder
    context.registerClass(
        LocalFolder.LocalFolder,
        constructors = (LocalFolder.manage_addLocalFolderForm,
                        LocalFolder.manage_addLocalFolder),
        icon='img/local_folder.gif')

    context.registerHelp()

    # Register the dtml-gettext tag
    String.commands['gettext'] = GettextTag
