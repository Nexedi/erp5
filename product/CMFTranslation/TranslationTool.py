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
from utils import _dtmldir, _translate_txt, _translate_html, _translate_stx
from Products.Localizer.Utils import lang_negotiator
from Products.Localizer.MessageCatalog import MessageCatalog
from BTrees.OOBTree import OOBTree
from zLOG import LOG

class TranslationError( Exception ):
    pass

class TranslationTool( UniqueObject, SimpleItem ):

    id              = 'portal_translations'
    meta_type       = 'CMF Translation Tool'

    security = ClassSecurityInfo()

    #
    #   Default values.
    #
    registered_translations = None

    def __init__( self ):
        self._registered_translations = OOBTree()
        self._translation_cache = OOBTree()        
        
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
    def findMessageCatalog(self, content, language=None, section=None):
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
        translation_path, translation = self.findRegisteredTranslation(content)
        if translation is not None:
            #LOG('Found Registered Translation',0,str(translation))
            return translation
            #return translation.getMessageCatalog()
        else:
            #LOG('Found No Registered Translation',0,'')
            # A default translation is provided if and only if no translation is set on the 
            # focument with default language
            return getattr(content, str(content.id) + '.msg' ,
                            getattr(content.Localizer, 'content', None))

    # Translation registration catalog
    # Can be improved a lot (of course)
    security.declarePublic( 'registerTranslation' )
    def registerTranslation(self, content, translation, translation_path, language=None, section=None):
        """
            This function allows to register a user translation
            
            content  --   A CMF document for which the translation
                          should be used
            
            translation -- A string containing a gettext formatted translation
                           definition

            translation_path -- a path to the document which holds the translation                                                      
                           
            language -- The language provided in translation
            
            section -- an optional string whenever multiple translations are required 
                       for a given                    
        """
        if translation is not None:
          # Build a new message catalog and import translation
          mc = MessageCatalog("mc", "Message Catalog", (language,))
          aq_mc = mc.__of__(self)
          aq_mc.manage_import(language, translation)                        
        else:
          mc = None          
        # Get the path of content and translation
        content_path = content.getPhysicalPath()
        # Register the path for content and translation for language
        if not self._registered_translations.has_key(content_path):
          self._registered_translations[content_path] = PersistentMapping()
        self._registered_translations[content_path][(language,section)] = (translation_path, mc)
    

    security.declarePublic( 'findRegisteredTranslation' )
    def findRegisteredTranslation(self, content, language=None, section=None):
        """
            This function allows to find if a translation has been registered
        """
        content_path = content.getPhysicalPath()
        #LOG('Lookup translation for',0,str(content_path))
        if self._registered_translations.has_key(content_path):
            # Find negociated language if necessary
            if language is None:
                language = lang_negotiator([content.language] +
                        map(lambda x:x[0], self._registered_translations[content_path].keys()))
                if language is None:
                    return None, None
            if self._registered_translations[content_path].has_key((language, section)):
              translation_path, mc = \
                self._registered_translations[content_path].get((language, section))
              #LOG('Found Translation %s for %s' % (translation_path,language),0,str(mc))  
            else:
                #LOG('No Translation Found',0,'')
                return None, None                
            if mc is None:
                #LOG('No Translation Found',0,'')
                return None, None
            else:
                #LOG('Translation Found',0,translation_path)
                return translation_path, mc
        else:
            #LOG('No Registered Translation Found',0,'')
            return None, None
    
    security.declarePublic( 'translateContent' )
    def translateContent(self, content, txt, language=None, section=None, format='txt'):
        """
            This function allows to find if a translation has been registered
        """
        content_path = content.getPhysicalPath()
        md = self.findMessageCatalog(content, language=language, section=section)
        if md is not None:
          if format == 'txt':
            return _translate_txt(txt, md)
          elif format == 'stx':
            return _translate_stx(txt, md)
          else:
            return _translate_html(txt, md)
        else:
          return txt
    
    security.declarePublic( 'getTranslationTemplate' )
    def getTranslationTemplate(self, content, view_method_id=None, section=None):
        """
            This function allows to find if a translation has been registered
        """
        content_path = content.getPhysicalPath()
        if not self._registered_translations.has_key(content_path):
          self._registered_translations[content_path] = PersistentMapping()
        # Use default language
        language = lang_negotiator([content.language] + 
                        map(lambda x:x[0], self._registered_translations[content_path].keys()))
        # Backup existing message catalog        
        backup = self._registered_translations[content_path].get((language,section))        
        # Create a new catalog
        mc = MessageCatalog('temp', 'Temporary Message Catalog', (language, )).__of__(self)
        # Associate it
        #LOG('Register translation for',0,str(content_path))
        self._registered_translations[content_path][(language,section)] = ('temp', mc)
        # Simulate rendering of page
        if view_method_id is None:
            content()
        else:
            getattr(content, view_method_id)()
        # Reset backup
        if backup is not None:
          self._registered_translations[content_path][(language,section)] = backup
        else:          
          del self._registered_translations[content_path][(language,section)]
        # And return the template
        return mc.manage_export('locale.pt')
                
    security.declarePublic( 'testTranslation' )
    def testTranslation(self, content, translation, view_method_id=None, section=None):
        """
            This function allows to register a user translation
            
            content  --   A CMF document for which the translation
                          should be used
            
            translation -- A string containing a gettext formatted translation
                           definition

            translation_path -- a path to the document which holds the translation                                                      
                           
            language -- The language provided in translation
            
            section -- an optional string whenever multiple translations are required 
                       for a given                    
        """
        content_path = content.getPhysicalPath()
        if not self._registered_translations.has_key(content_path):
          self._registered_translations[content_path] = PersistentMapping()
        # Use default language
        language = lang_negotiator([content.language] + 
                        map(lambda x:x[0], self._registered_translations[content_path].keys()))
        # Backup existing message catalog        
        backup = self._registered_translations[content_path].get((language,section))        
        # Create a new catalog
        # Build a new message catalog and import translation
        mc = MessageCatalog("mc", "Message Catalog", (language,))
        aq_mc = mc.__of__(self)
        aq_mc.manage_import(language, translation)                        
        # Associate it
        #LOG('Register translation for',0,str(content_path))
        self._registered_translations[content_path][(language,section)] = ('temp', mc)
        # Simulate rendering of page
        if view_method_id is None:
            result = content()
        else:
            result = getattr(content, view_method_id)()
        # Reset backup
        if backup is not None:
          self._registered_translations[content_path][(language,section)] = backup
        else:          
          del self._registered_translations[content_path][(language,section)]
        # And return the translated page
        return result
                

InitializeClass( TranslationTool )
