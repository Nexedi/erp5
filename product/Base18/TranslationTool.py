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
__doc__ = "This product provides the basic behaviour to CMF object which need\
 translation"


"""\
Base18 portal_translation tool.
"""

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass, DTMLFile, PersistentMapping
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore import CMFCorePermissions
from utils import _dtmldir
from Products.Localizer.Utils import lang_negotiator

#import zLOG

class TranslationError( Exception ):
    pass

class TranslationTool( UniqueObject, SimpleItem ):

    id              = 'portal_translations'
    meta_type       = 'Base18 Translation Tool'

    security = ClassSecurityInfo()

    #
    #   Default values.
    #
    registered_translations = None

    def __init__( self ):
        self.registered_translations = PersistentMapping()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                       , { 'label'      : 'Properties'
                         , 'action'     : 'propertiesForm'
                         }
                       )
                     + SimpleItem.manage_options
                     )

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainTranslationTool', _dtmldir )

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'propertiesForm' )
    propertiesForm = DTMLFile( 'translationProperties', _dtmldir )

    security.declareProtected( CMFCorePermissions.ManagePortal
                             , 'editProperties' )
    def editProperties( self
                      , publisher=None
                      , REQUEST=None
                      ):
        """
            Form handler for "tool-wide" properties (including list of
            metadata elements).
        """
        if publisher is not None:
            self.publisher = publisher

        if REQUEST is not None:
            REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                                        + '/propertiesForm'
                                        + '?manage_tabs_message=Tool+updated.'
                                        )

    #
    #   'portal_translations' interface
    #

    security.declarePublic( 'findMessageCatalog' )
    def findMessageCatalog(self, content, language=None):
        """
            Return the default message catalog for
            an object to translate
            For now, look in the same directory
            or in the acquisition path either for a message catalog for
            that object or for a message more global catalog
            In the future, we will try to look at message catalogs provided by
            users.

            A workklow will be used to manage the status of translations
        """
        translation = self.findRegisteredTranslation(content)
        if translation is not None:
            return translation.getMessageCatalog()
        else:
            return getattr(content.aq_parent, str(content.id) + '.msg' ,
                            content.gettext)

    # Translation registration catalog
    # Can be improved a lot (of course)
    security.declarePublic( 'registerTranslation' )
    def registerTranslation(self, content, translation, language=None):
        """
            This function allows to register a user translation
        """
        # If language not supplied, look up languages in the user translation
        if language is None:
            languages = translation.getMessageCatalog().get_languages()
        else:
            languages=(language,)
        # Get the path of content and translation
        content_path = content.getPhysicalPath()
        translation_path = translation.getPhysicalPath()
        # Register the path for content and translation for each available
        # language
        if not self.registered_translations.has_key(content_path):
            self.registered_translations[content_path] = PersistentMapping()
        for lang in languages:
            self.registered_translations[content_path][lang] = translation_path
    
    security.declarePublic( 'unregisterTranslation' )
    def unregisterTranslation(self, content, translation=None, language=None):
        """
            This function allows to register a user translation
        """
        content_path = content.getPhysicalPath()
        # Is content registered ?
        if self.registered_translations.has_key(content_path):
            if language is None:
                languages = self.registered_translations[content_path].keys()
            else:
                if self.registered_translations[content_path].has_key(language):
                    languages = (language,)
                else:
                    languages = []
            if translation is not None:
                translation_path = translation.getPhysicalPath()
            for lang in languages:
                # If no translation provided, then remove default translation
                if translation is None:
                    del self.registered_translations[content_path][lang]
                # if translation is provided, remove that translation only
                else:
                    if self.registered_translations[content_path][lang] == \
                                                    translation_path:
                        del self.registered_translations[content_path][lang]
        else:
            pass

    security.declarePublic( 'findRegisteredTranslation' )
    def findRegisteredTranslation(self, content, language=None):
        """
            This function allows to find if a translation has been registered
        """
        content_path = content.getPhysicalPath()
        if self.registered_translations.has_key(content_path):
            # Find negociated language if necessary
#            zLOG.LOG('Registered Translation Found',0,content_path)
            if language is None:
                language = lang_negotiator([content.language] +
                        self.registered_translations[content_path].keys())
#                zLOG.LOG('Neg. Language',0,self.language + ',' + language)
                if language is None:
                    return None
            translation_path = \
                self.registered_translations[content_path].get(language, None)
            if translation_path is None:
#               zLOG.LOG('No Translation Path Found',0,translation_path)
                return None
            else:
#               zLOG.LOG('Translation Path Found',0,translation_path)
                try: return self.restrictedTraverse(translation_path)
                except: return None
        else:
#            zLOG.LOG('No Registered Translation Found',0,content_path)
            return None
    
    
InitializeClass( TranslationTool )
