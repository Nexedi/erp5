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
from Products.ERP5Type.Base import Base
from Products.CMFPhoto.CMFPhoto import CMFPhoto
from Products.Photo.Photo import Photo


class Image (Base, CMFPhoto):
  """
    An Image can contain text that can be formatted using
    *Structured Text* or *HTML*. Text can be automatically translated
    through the use of 'message catalogs'.

    A Document is a terminating leaf
    in the OFS. It can not contain anything.

    Document inherits from XMLObject and can
    be synchronized accross multiple sites.
  """

  meta_type = 'ERP5 Image'
  portal_type = 'Image'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )

  def __init__( self, id, title='', file='', store='ExtImage'
              , engine='ImageMagick', quality=75, pregen=0, timeout=0):
    Photo.__init__(self, id=id, title=title, file=file, store=store
                  , engine=engine, quality=quality, pregen=pregen, timeout=timeout)
    Base.__init__(self, id=id)
    self._data = ''
    self.store = store

  ### Special edit method
  security.declarePrivate('_edit')
  def _edit(self, **kw):
    """
      This is used to edit files
    """
    if not hasattr(self, '_original'):
      if self.store   == 'Image'   : from Products.Photo.PhotoImage    import PhotoImage
      elif self.store == 'ExtImage': from Products.Photo.ExtPhotoImage import PhotoImage
      self._original = PhotoImage(self.id, self.title, path=self.absolute_url(1))
    if kw.has_key('file'):
      file = kw.get('file')
      precondition = kw.get('precondition')
      CMFPhoto.manage_editPhoto(self, file=file)
      self.manage_purgeDisplays()
      del kw['file']
    Base._edit(self, **kw)

  security.declareProtected('View', 'index_html')
  index_html = CMFPhoto.index_html

  security.declareProtected('AccessContentsInformation', 'content_type')
  content_type = CMFPhoto.content_type

  # Copy support needs to be implemented by ExtFile
  ################################
  # Special management methods   #
  ################################

  def manage_afterClone(self, item):
    Base.manage_afterClone(self, item)
    CMFPhoto.manage_afterClone(self, item)

  def manage_afterAdd(self, item, container):
    CMFPhoto.manage_afterAdd(self, item, container)

  def manage_beforeDelete(self, item, container):
    CMFPhoto.manage_beforeDelete(self, item, container)

  # Some ERPish
  def getWidth(self):
    """
      Alias for width
    """
    return self.width()

  def getHeight(self):
    """
      Alias for width
    """
    return self.height()

  # Aliases for uniform update of data
  def manage_upload(self, file='', REQUEST=None):
    self.manage_file_upload(self, file=file, REQUEST=None)