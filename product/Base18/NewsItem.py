##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
__version__ = "$Revision$"[11:-2]
__doc__ = "This product provides multilingual capabilities to the CMFDefault NewsItem"


from utils import _translate_stx
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.Localizer.MessageCatalog import MessageCatalog

from Products.CMFDefault.NewsItem import NewsItem

from Base18 import Base18
from Document import Document18

from zLOG import LOG

import commands

# Content Creator
def addNewsItem18( self
               , id
               , title=''
               , description=''
               , text=''
               , text_format='html'
               ):
    """
        Add a Multilingual NewsItem
    """
    o=NewsItem18( id=id
              , title=title
              , description=description
              , text=text
              , text_format=text_format
              )
    self._setObject(id, o)

# Content Class
class NewsItem18(NewsItem, Document18):
    """ A Multilingual NewsItem - Handles both StructuredText and HTML
        and translates sentences through a portal_translations tool
    """
    meta_type = 'Base18 News Item'
    portal_type = 'News Item'

    # Declarative security (replaces __ac_permissions__)
    security = ClassSecurityInfo()

    # CMF Factory Type Information
    factory_type_information = ( { 'id'             : portal_type
                                 , 'meta_type'      : meta_type
                                 , 'description'    : """\
News Items contain short text articles and carry a title as well as an optional description.\
Text can be automatically translated through the use of message catalogs."""
                                 , 'icon'           : 'newsitem_icon.gif'
                                 , 'product'        : 'Base18'
                                 , 'factory'        : 'addNewsItem18'
                                 , 'immediate_view' : 'metadata_edit_form'
                                 , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'newsitem18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'print'
                                  , 'name'          : 'Print'
                                  , 'action'        : 'newsitem18_print'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'mail'
                                  , 'name'          : 'Mail'
                                  , 'action'        : 'newsitem_mail_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                               , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'newsitem_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'translate'
                                  , 'name'          : 'Translate'
                                  , 'action'        : 'translation_template'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                )
                             }
                           ,
                           )

    security.declareProtected(CMFCorePermissions.View, 'PreformattedView')
    def PreformattedView(self):
        """
            Return a preformatted rendering of this news
            Useful to send by email
        """
        LOG('Pref',0, self.local_absolute_url())
        result = commands.getoutput("lynx -dump %s/newsitem18_print" % self.local_absolute_url())
        LOG('Pref',0,str(result))
        return result


InitializeClass( NewsItem18 )

