##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
__doc__ = "This product provides multilingual capabilities to the CMFDefault \
 Document"

import os

from utils import _translate_stx, _translate_html
from Globals import InitializeClass, PersistentMapping, package_home
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore import CMFCorePermissions
from Products.Localizer.MessageCatalog import MessageCatalog

from Products.CMFDefault.Document import Document
from Products.CMFWiki import CMFWikiPage, CMFWikiPermissions
from Products.CMFWiki.CMFWikiPage import initPageMetadata, default_perms, \
     thunk_substituter
from Products.CMFWiki.ZWikiRegexes import urlchars, url, urlexp, bracketedexpr,\
     bracketedexprexp, underlinedexpr, underlinedexprexp, wikiname1,\
     wikiname2, simplewikilinkexp, wikiending, urllinkending, wikilink,\
     wikilinkexp, wikilink_, interwikilinkexp, remotewikiurlexp,\
     protected_lineexp, antidecaptext, antidecapexp, commentsdelim,\
     preexp, unpreexp, citedexp, cite_prefixexp, intl_char_entities
from Products.CMFCore.utils import _getViewFor
from Acquisition import aq_base, aq_inner, aq_parent

from Base18 import Base18
from Document import Document18

from utils import _translate_stx

import zLOG


# Content Constructor
def makeCMFWikiPage18(id, title, file):
    ob = CMFWikiPage18(source_string=file, __name__=id)
    ob.title = title
    ob.parents = []
    username = getSecurityManager().getUser().getUserName()
    ob.manage_addLocalRoles(username, ['Owner'])
    ob.setSubOwner('both')
    initPageMetadata(ob)
    for name, perm in ob._perms.items():
        pseudoperm = default_perms[name]
        local_roles_map = ob._local_roles_map
        roles_map = ob._roles_map
        roles = (local_roles_map[name],) + roles_map[pseudoperm]
        ob.manage_permission(perm, roles=roles)
    return ob

def addCMFWikiPage18(self, id, title='', file=''):
    id=str(id)
    title=str(title)
    ob = makeCMFWikiPage18(id, title, file)
    self._setObject(id, ob)

# Content Class
class CMFWikiPage18(CMFWikiPage.CMFWikiPage, Document18):
    """ A Multilingual Document - Handles both StructuredText and HTML
        and translates sentences through a portal_translations tool
    """
    meta_type = 'Base18 Wiki Page'
    portal_type = 'Wiki Page'
    isPortalContent = 1

    # Default values
    cached_translations = None

    # Declarative security
    security = ClassSecurityInfo()

    # CMF Factory Type Information
    factory_type_information = \
      {'id': portal_type,
       'content_icon': 'wikipage_icon.gif',
       'meta_type': meta_type,
       'product': 'Base18',
       'factory': 'addCMFWikiPage18',
       'immediate_view': 'wikipage_view',
       'actions': ({'id': 'view',
                    'name': 'View',
                    'action': 'wikipage_view',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'comment',
                    'name': 'Comment',
                    'action': 'wikipage_comment_form',
                    'permissions': (CMFWikiPermissions.Comment,)},
                   {'id': 'edit',
                    'name': 'Edit',
                    'action': 'wikipage_edit_form',
                    'permissions': (CMFWikiPermissions.Edit,)},
                   {'id': 'translate',
                    'name': 'Translate',
                    'action': 'translation_template',
                    'permissions': (CMFWikiPermissions.Edit,)},
                   {'id': 'history',
                    'name': 'History',
                    'action': 'wikipage_history',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'backlinks',
                    'name': 'Backlinks',
                    'action': 'wikipage_backlinks',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'advanced',
                    'name': 'Advanced',
                    'action': 'wikipage_advanced_form',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'toc',
                    'name': 'Wiki Contents',
                    'category': 'folder',
                    'action':'wikipage_toc',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'recent_changes',
                    'name': 'Recent Changes',
                    'category': 'folder',
                    'action':'wikipage_recentchanges',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'create',
                    'name': 'Create',
                    'category': 'folder',
                    'action':'wikipage_create_form',
                    'permissions': (CMFWikiPermissions.Create,),
                    'visible': 0 },
                   ),
       }

    # Fixed Methods
    def Title(self): # for CMFCatalog
        return self.title_or_id()

    # New Rendering Method
    def render_structuredtext(self, client=None, REQUEST={},
                              RESPONSE=None, **kw):
        # structured text + wiki links + HTML
        if kw.has_key('level'):
	    t =  self.TranslatedBody(stx_level = kw['level'])
	else:
	    t = self.TranslatedBody()
        #t = protected_lineexp.sub(self._protect_line, t)
        #if self._st_data is None:
            # XXX klm: Shouldn't happen -_st_data should've been set by edit.
        #    t = str(html_with_references(t, level=3))
        t = interwikilinkexp.sub(
            thunk_substituter(self._interwikilink_replace, t, 1),
            t)
        t = wikilinkexp.sub(thunk_substituter(self._wikilink_replace, t,
                            self.isAllowed('create')), t)
        return t

    RENDERERS = {
    'structuredtext'      : render_structuredtext
  , 'structuredtextonly'  : CMFWikiPage.CMFWikiPage.render_structuredtextonly
  , 'html'                : CMFWikiPage.CMFWikiPage.render_html
  , 'classicwiki'         : CMFWikiPage.CMFWikiPage.render_classicwiki
  , 'plaintext'           : CMFWikiPage.CMFWikiPage.render_plaintext
                }

    ### Content accessor methods
    security.declareProtected(CMFCorePermissions.View, 'SearchableText')
    def SearchableText(self, md=None):
        """\
        Used by the catalog for basic full text indexing
        We are going to concatenate all available translations
        """
        if md is None: md = self.findMessageCatalog()
        searchable_text = ""
        for lang in md.get_languages():
            searchable_text = searchable_text + "%s %s %s" %  (
                              md.gettext(self.Title(),lang)
                            , md.gettext(self.Description(),lang)
                            , self.TranslatedBody(lang=lang)
                            )
        return searchable_text

# Content Constructor
def addCMFWikiFolder18(self, id, title=''):
    id = str(id)
    title = str(title)
    ob = CMFWikiFolder18(id, title)
    id = self._setObject(id, ob)
    ob = getattr(self, id)
    p = package_home(globals()) + os.sep + 'default_wiki_content'
    fnames = os.listdir(p)
    for fname in fnames:
        if fname[-5:] != '.wiki': continue
        f = open(p + os.sep + fname, 'r')
        fname = fname[:-5]
        addCMFWikiPage18(ob, fname, title='', file=f.read())
        page = getattr(ob, fname)
        page.indexObject()
        # Hack - may be ok if we continue to have, like, only two pages:
        if fname == 'SandBox':
            page.parents = ['FrontPage']

# Content Class
class CMFWikiFolder18( CMFWikiPage.CMFWikiFolder, Base18 ):
    meta_type = 'Base18 Wiki'
    portal_type = 'Wiki'
    isPortalContent = 1

    # Default values
    cached_translations = None

    # Declarative security
    security = ClassSecurityInfo()

    # CMF Factory Type Information
    factory_type_information = \
      {'id': portal_type,
       'content_icon': 'folder_icon.gif',
       'meta_type': meta_type,
       'description': ('Loosely organized (yet structured) content can be '
                       'added to Wikis.'),
       'product': 'Base18',
       'factory': 'addCMFWikiFolder18',
       'immediate_view': 'FrontPage',
       'actions': ({'id': 'toc',
                    'name': 'Wiki Contents',
                    'category': 'folder',
                    'action':'wiki_toc',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'view',
                    'name': 'FrontPage',
                    'category': 'folder',
                    'action':'FrontPage',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'edit',
                    'name': 'Edit',
                    'category': 'folder',
                    'action':'folder_edit_form',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'all',
                    'name': 'All Pages',
                    'category': 'folder',
                    'action':'wiki_allpages',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'recent_changes',
                    'name': 'Recent Changes',
                    'category': 'folder',
                    'action':'wiki_recentchanges',
                    'permissions': (CMFWikiPermissions.View,)},
                   {'id': 'wikihelp',
                    'name': 'WikiHelp',
                    'category': 'folder',
                    'action': 'WikiHelp',
                    'permissions': (CMFWikiPermissions.View,)}
                   ),
       },

    security.declareProtected(CMFWikiPermissions.View, '__call__')
    def __call__(self, client=None, REQUEST=None, RESPONSE=None, **kw):
        '''
        Invokes the default view.
        '''
        if RESPONSE is not None:
          return RESPONSE.redirect(self.absolute_url() + '/FrontPage' )
        if REQUEST is not None:
          return REQUEST.RESPONSE.redirect(self.absolute_url() + '/FrontPage' )
        else:
          REQUEST = {}
        view = _getViewFor( self )
        if getattr(aq_base(view), 'isDocTemp', 0):
            return apply(view, (self, REQUEST))
        else:
            if REQUEST:
                kw[ 'REQUEST' ] = REQUEST
            if RESPONSE:
                kw[ 'RESPONSE' ] = RESPONSE

            return apply( view, (self,), kw )

    index_html = None  # This special value informs ZPublisher to use __call__


InitializeClass(CMFWikiPage18)
InitializeClass(CMFWikiFolder18)
CMFWikiPage = CMFWikiPage18
CMFWikiFolder = CMFWikiFolder18
addCMFWikiPage = addCMFWikiPage18
addCMFWikiFolder = addCMFWikiFolder18


