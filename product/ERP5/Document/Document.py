##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject

from Products.Base18.Document import Document as Document18
from Products.Base18.interfaces.Translatable import Translatable

class Document(XMLObject, Document18):
    """
        A Document can contain text that can be formatted using
        *Structured Text* or *HTML*. Text can be automatically translated
        through the use of 'message catalogs'.

        A Document is a terminating leaf
        in the OFS. It can not contain anything.

        Document inherits from XMLObject and can
        be synchronized accross multiple sites.
    """

    meta_type = 'ERP5 Document'
    portal_type = 'Document'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Document
                      )

    # Declarative interfaces
    __implements__ = ( Translatable )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Document can contain text that can be formatted using 'Structured Text'.\
or 'HTML'. Text can be automatically translated through the use of\
'message catalogs' and provided to the user in multilple languages."""
         , 'icon'           : 'document_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDocument'
         , 'immediate_view' : 'document_edit'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'document_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'edit'
          , 'name'          : 'Edit'
          , 'category'      : 'object_view'
          , 'action'        : 'document_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'document_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    ### Content accessor methods
    security.declareProtected(Permissions.View, 'SearchableText')
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

    ### Specific Translation methods
    security.declareProtected(Permissions.View, 'TranslatedBody')
    def TranslatedBody(self, stx_level=None, setlevel=0, lang=None, md=None):
        """\
        Equivalent to CookedBody but returns a translated version thanks
        to the use of message catalog
        """
        if md is None: md = self.findMessageCatalog()
        if stx_level is None: stx_level = self._stx_level
        if lang is None: lang = self.getNegotiatedLanguage(md)
        # Create a translation cache if necessary
        if self.cached_translations is None:
            self.cached_translations = PersistentMapping()
        if not self.cached_translations.has_key(lang) or \
                            stx_level != self._stx_level:
            if self.text_format == 'html':
                cooked = _translate_html(self.text_content, md, stx_level, lang)
            else:
                cooked = _translate_stx(self.text_content, md, stx_level, lang)
            self.cached_translations[lang] = \
                    (md.bobobase_modification_time(),cooked)
        elif self.cached_translations[lang][0] != \
                    md.bobobase_modification_time()  or \
                    self.cached_translations[lang][1] != \
                    self.bobobase_modification_time():
            if self.text_format == 'html':
                cooked = _translate_html(self.text_content, md, stx_level, lang)
            else:
                cooked = _translate_stx(self.text_content, md, stx_level, lang)
            self.cached_translations[lang] = (md.bobobase_modification_time(),
                self.bobobase_modification_time(),cooked)
        else:
            cooked = self.cached_translations[lang][2]
        return cooked

    security.declareProtected(Permissions.View, 'TranslationTemplate')
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
        cooked = _translate_stx(self.text_content, md, self._stx_level, None)
        md.gettext(self.Title())
        md.gettext(self.Description())
        # And return the template
        return md.manage_export('locale.pt')
