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
__doc__ = "This product provides multilingual capabilities to the CMFDefault \
 Document"

from utils import _translate_stx, _translate_html
from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.Localizer.MessageCatalog import MessageCatalog

from Products.CMFDefault.Document import Document

from Base18 import Base18

#import zLOG

# Content Creator
def addDocument18(self, id, title='', description='', text_format='',
                text=''):
    """ Add a Multilingual Document """
    o = Document18(id, title, description, text_format, text)
    self._setObject(id,o)

# Content Class    
class Document18(Document,Base18):
    """ A Multilingual Document - Handles both StructuredText and HTML
        and translates sentences through a portal_translations tool
    """
    meta_type = 'Base18 Document'
    portal_type = 'Document'
    isPortalContent = 1

    # Default values
    cached_translations = None

    # Declarative security
    security = ClassSecurityInfo()

    # CMF Factory Type Information
    factory_type_information = ( { 'id'             : portal_type
                                 , 'meta_type'      : meta_type
                                 , 'description'    : """\
Document can contain text that can be formatted using 'Structured Text.\
Text can be automatically translated through the use of message catalogs.'"""
                                 , 'icon'           : 'document_icon.gif'
                                 , 'product'        : 'Base18'
                                 , 'factory'        : 'addDocument18'
                                 , 'immediate_view' : 'metadata_edit_form'
                                 , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'document18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'print'
                                  , 'name'          : 'Print'
                                  , 'action'        : 'document18_print'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'document_edit_form'
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

    # Source Text access
    security.declareProtected(CMFCorePermissions.View, 'getText')
    def getText(self):
        """
          Returns source text
        """
        return self.text

    # Specific Translation methods
    security.declareProtected(CMFCorePermissions.View, 'TranslatedBody')
    def TranslatedBody(self, stx_level=None, setlevel=0, lang=None, md=None):
        """\
        Equivalent to CookedBody but returns a translated version thanks
        to the use of message catalog
        """
        if md is None: md = self.findMessageCatalog()
        if stx_level is None: stx_level = self._stx_level
        if lang is None: lang = self.getNegotiatedLanguage(md)
        #zLOG.LOG('Language',0,lang)
        # Create a translation cache if necessary
        if self.cached_translations is None:
            self.cached_translations = PersistentMapping()
        if not self.cached_translations.has_key(lang) or \
                            stx_level != self._stx_level:
            if self.text_format == 'html':
                cooked = _translate_html(self.text, md, stx_level, lang)
            else:
                cooked = _translate_stx(self.text, md, stx_level, lang)
            self.cached_translations[lang] = \
                    (md.bobobase_modification_time(),cooked)
        elif self.cached_translations[lang][0] != \
                    md.bobobase_modification_time()  or \
                    self.cached_translations[lang][1] != \
                    self.bobobase_modification_time():
            if self.text_format == 'html':
                cooked = _translate_html(self.text, md, stx_level, lang)
            else:
                cooked = _translate_stx(self.text, md, stx_level, lang)
            self.cached_translations[lang] = (md.bobobase_modification_time(),
                self.bobobase_modification_time(),cooked)
        else:
            cooked = self.cached_translations[lang][2]
        return cooked

    security.declareProtected(CMFCorePermissions.View, 'TranslationTemplate')
    def TranslationTemplate(self):
        """\
        This method allows to produce of .pot file for this document
        """
        # Create a new catalog
        md = MessageCatalog('temp', 'Temporary Message Catalog',
            self.findMessageCatalog().get_languages())
        # Do some dirty acquisition trick
        md.aq_base = self
        # Run the md on the text body, title and description
        cooked = _translate_stx(self.text, md, self._stx_level, None)
        md.gettext(self.Title())
        md.gettext(self.Description())
        # And return the template
        return md.manage_export('locale.pt')


InitializeClass(Document18)
Document = Document18
