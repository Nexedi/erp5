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

from utils import _translate_stx
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions, PortalContent
from Products.Localizer.MessageCatalog import MessageCatalog

from Document import Document18
import string

# Content Creator
def addTranslation(self, id, title='', description=''):
    """ Add a Translation Document """
    o = Translation(id, title, description)
    self._setObject(id,o)

# Content Class
class Translation(Document18):
    """ A User Translation Document managed by the CMF
        Actually, just a wrapper arround Localize to
        make it editable under the CMF
    """
    meta_type = 'Base18 Translation'

    # Declarative security
    security = ClassSecurityInfo()

    # CMF Factory Type Information
    factory_type_information = ( { 'id'             : 'Translation'
        , 'meta_type'      : 'Base18 Translation'
        , 'description'    : """\
Translations can contain a list of translation messages formatted according\
to the .po standard. Translations can be registered through a translation\
workflow and provide a translation to an existing document in a portal'"""
        , 'icon'            :   'document_icon.gif'
        , 'product'         :   'Base18'
        , 'factory'         :   'addTranslation'
        , 'immediate_view'  :   'metadata_edit_form'
        , 'actions'         :   ( { 'id'             : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'translation_view'
                                  , 'permissions'   : (CMFCorePermissions.View,)
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'translation_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'template'
                                  , 'name'          : 'Translation Template'
                                  , 'action'        : 'translation_template'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                )
                             }
                           ,
                           )

    ### Default values
    targetContent = ()
    targetLanguage = ('en')
    messageCatalog = None

    ### Edit method
    security.declareProtected( CMFCorePermissions.ModifyPortalContent, 'edit' )
    def edit( self
            , text_format
            , text
            , file=''
            , safety_belt=''
            , target_language='en'
            , target_content=None
            ):
        """
        *used to be WorkflowAction(_edit)
        To add webDav support, we need to check if the content is locked, and if
        so return ResourceLockedError if not, call _edit.

        Note that this method expects to be called from a web form, and so
        disables header processing
        """
        self.targetLanguage = target_language
        if target_content is not None:
            self.targetContent = target_content.getPhysicalPath()
        else:
            self.targetContent = ('a')
        Document18.edit(self, text_format, text, file, safety_belt)
        self.messageCatalog = MessageCatalog("mc", "Message Catalog",
                                (self.targetLanguage,))
        self.messageCatalog.manage_import(self.targetLanguage, self.text)

    def _edit(self, text, text_format='', safety_belt=''):
        """ Edit the Document - Parses headers and cooks the body"""
        headers = {}
        if not safety_belt:
            safety_belt = headers.get('SafetyBelt', '')
        if not self._safety_belt_update(safety_belt=safety_belt):
            msg = ("Intervening changes from elsewhere detected."
                   " Please refetch the document and reapply your changes."
                   " (You may be able to recover your version using the"
                   " browser 'back' button, but will have to apply them"
                   " to a freshly fetched copy.)")
            raise 'EditingConflict', msg
        self.text = self.cooked_text = text        

    ### Content accessor methods
    security.declareProtected(CMFCorePermissions.View, 'SearchableText')
    def SearchableText(self, md=None):
        """\
        Used by the catalog for basic full text indexing
        We are going to concatenate all available translations
        """
        if md is None: md = self.findMessageCatalog()
        searchable_text = self.text
        for lang in md.get_languages():
            searchable_text = searchable_text + "%s %s" %  (
                            md.gettext(self.Title(),lang)
                            , md.gettext(self.Description(),lang)
                            )
        return searchable_text

    # Translation methods
    security.declareProtected(CMFCorePermissions.View, 'TranslatedBody')
    def TranslatedBody(self, stx_level=None, setlevel=0, lang=None, md=None):
        """\
        Equivalent to CookedBody but returns a translated version thanks
        to the use of message catalog
        """
        if md is None: md = self.find_md()
        if stx_level is None: stx_level = self._stx_level
        cooked = _translate_stx(self.text, md, stx_level, lang)
        return cooked           

    security.declareProtected(CMFCorePermissions.View, 'TranslationTemplate')
    def TranslationTemplate(self):
        """\
        This method allows to produce of .pot file for this document
        """
        # Create a new catalog
        md = MessageCatalog('temp', 'Temporary Message Catalog',
                        self.find_md().get_languages())
        # Do some dirty acquisition trick
        md.aq_base = self
        # Run the md on the text body
        cooked = _translate_stx(self.text, md, self._stx_level, None)
        md.gettext(self.Title())
        md.gettext(self.Description())
        # And return the template
        return md.manage_export('locale.pt')

    # Implementation with Message Catalogs
    security.declareProtected(CMFCorePermissions.View, 'getMessageCatalog')   
    def getMessageCatalog(self):
        return self.messageCatalog

    security.declareProtected(CMFCorePermissions.View, 'targetContentPath')
    def targetContentPath(self):
        return string.join(self.targetContent,'/')
    
InitializeClass(Translation)
