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
# TODO:
#      - Implement Vary so that cache can take into account translated version
#      - Implement language caching....
#
##############################################################################
"""
"""

ADD_CONTENT_PERMISSION = 'Add portal content'

import Document, NewsItem, Replica, Translation, Wiki
import TranslationTool, MembershipTool, CookieCrumbler

from Products.CMFCore import utils
import Products.CMFCore
from Products.CMFCore.DirectoryView import registerDirectory

contentClasses = ( Document.Document18
                 , NewsItem.NewsItem18
                 , Replica.File18
                 , Replica.Link18
                 , Replica.Image18
                 , Replica.Favorite18
                 , Replica.DiscussionItem18
                 , Replica.SkinnedFolder18
                 , Translation.Translation
                 , Wiki.CMFWikiPage18
                 , Wiki.CMFWikiFolder18
                    )


contentConstructors = ( Document.addDocument18
                      , NewsItem.addNewsItem18
                      , Replica.addFile18
                      , Replica.addLink18
                      , Replica.addImage18
                      , Replica.addFavorite18
                      , Replica.addDiscussionItem18
                      , Replica.addSkinnedFolder18
                      , Translation.addTranslation
                      , Wiki.addCMFWikiPage18
                      , Wiki.addCMFWikiFolder18
                      )

contentFactoryTypeInformations = []
for content in contentClasses:
    if type(content.factory_type_information) == type({}):
      contentFactoryTypeInformations.append(content.factory_type_information)
    else:
      contentFactoryTypeInformations.append(content.factory_type_information[0])

tools = ( TranslationTool.TranslationTool
        , MembershipTool.MembershipTool18
        )

bases = contentClasses

import sys
this_module = sys.modules[ __name__ ]

z_bases = utils.initializeBasesPhase1( bases, this_module )
z_tool_bases = utils.initializeBasesPhase1( tools, this_module )

base18_globals=globals()

# Make the skins available as DirectoryViews.
registerDirectory('skins', globals())
registerDirectory('help', globals())

def initialize( context ):

    utils.initializeBasesPhase2( z_bases, context )
    utils.initializeBasesPhase2( z_tool_bases, context )
    
    utils.ToolInit('Base18 Tool', tools=tools,
                   product_name='Base18', icon='tool.png',
                   ).initialize( context )

    utils.ContentInit( 'Base18 Content'
                     , content_types=contentClasses
                     , permission=ADD_CONTENT_PERMISSION
                     , extra_constructors=contentConstructors
                     , fti=contentFactoryTypeInformations
                     ).initialize( context )    

    context.registerHelp()
    context.registerHelpTitle('Base18 Help')

