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

from OFS.Folder import Folder
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.PortalFolder import PortalFolder
from AccessControl import ClassSecurityInfo
from Products.Localizer.Utils import lang_negotiator

from utils import _translate_stx

from zLOG import LOG

class Base18(PortalContent):
   """ Base18 implements the basic translation tactics"""

   # Declarative security
   security = ClassSecurityInfo()

   ### Delegate to central repository
   def findMessageCatalog(self):
      return self.portal_translations.findMessageCatalog(self)

   ### Common translation methods
   security.declareProtected(CMFCorePermissions.View, 'TranslatedDescription')
   def TranslatedDescription(self):
      """
        Returns translated desc
      """
      return self.findMessageCatalog().gettext(self.Description())

   security.declareProtected(CMFCorePermissions.View, 'getTranslatedDescription')
   getTranslatedDescription = TranslatedDescription

   security.declareProtected(CMFCorePermissions.View, 'TranslatedTitle')
   def TranslatedTitle(self):
      """
          Returns a translated title
      """
      #LOG('TranslatedTitle',0,str(self))
      return self.findMessageCatalog().gettext(self.Title())

   security.declareProtected(CMFCorePermissions.View, 'getTranslatedTitle')
   getTranslatedTitle = TranslatedTitle

   security.declareProtected(CMFCorePermissions.View, 'TranslatedTitle_or_id')
   def TranslatedTitle_or_id(self):
      """
          Returns a translated title if title exists
          or id otherwise
      """
      title=self.title
      if callable(title):
          title=title()
      if title: return self.findMessageCatalog().gettext(title)
      return self.getId()

   security.declareProtected(CMFCorePermissions.View, 'getTranslatedTitle_or_id')
   getTranslatedTitle_or_id = TranslatedTitle_or_id

   security.declareProtected(CMFCorePermissions.View, 'getNegotiatedLanguage')
   def getNegotiatedLanguage(self,md=None):
      if md is None: md = self.findMessageCatalog()
      available_languages = list(md._languages)
      # Get the language!
      lang = lang_negotiator(available_languages)
      # Is it None? use the default
      if lang is None:
         lang = md._default_language
      return lang

   ### Generic Translation methods
   security.declareProtected(CMFCorePermissions.View, 'TranslatedBody')
   def TranslatedBody(self, stx_level=None, setlevel=0, lang=None, md=None):
      """\
      Equivalent to CookedBody but returns a translated version thanks
      to the use of message catalog
      """
      if md is None: md = self.findMessageCatalog()
      if stx_level is None:
            stx_level = self._stx_level
      cooked = _translate_stx(self.text, md, stx_level, lang)
      return cooked

   security.declareProtected(CMFCorePermissions.View, 'getTranslatedBody')
   getTranslatedBody = TranslatedBody

   # Catalog Related Method (required for ERP5)
   def getObject(self, REQUEST=None):
      """Returns self - useful for ListBox"""
      return self

# For Compatibility Purpose
PortalContent.getTranslatedTitle = Base18.TranslatedTitle
PortalContent.TranslatedTitle = Base18.TranslatedTitle
PortalContent.getTranslatedTitle_or_id = Base18.TranslatedTitle_or_id
PortalContent.TranslatedTitle_or_id = Base18.TranslatedTitle_or_id

PortalFolder.getTranslatedTitle = PortalContent.title_or_id
PortalFolder.TranslatedTitle = PortalContent.title_or_id
PortalFolder.getTranslatedTitle_or_id = PortalFolder.title_or_id
PortalFolder.TranslatedTitle_or_id = PortalFolder.title_or_id

Folder.getTranslatedTitle = Folder.title_or_id
Folder.TranslatedTitle = Folder.title_or_id
Folder.getTranslatedTitle_or_id = Folder.title_or_id
Folder.TranslatedTitle_or_id = Folder.title_or_id
