##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
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
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
__version__ = "$Revision$"[11:-2]
__doc__ = "This file provides an empty subclass on all CMFDefault content \
 classes"

from Globals import InitializeClass
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
#from AccessControl import ClassSecurityInfo

from Base18 import Base18
from Document import Document18

# Link Empty Sublass
from Products.CMFDefault import Link

def addLink18( self
           , id
           , title=''
           , remote_url=''
           , description=''
           ):
    """
        Add a Link instance to 'self'.
    """
    o=Link18( id, title, remote_url, description )
    self._setObject(id,o)

class Link18(Link.Link, Base18):
    meta_type = 'Base18 Link'
    portal_type = 'Link'
    isPortalContent = 1
    factory_type_information = ( { 'id'         : portal_type
                             , 'meta_type'      : meta_type
                             , 'description'    : """\
Link items are URLs that come with additional information."""
                             , 'icon'           : 'link_icon.gif'
                             , 'product'        : 'Base18'
                             , 'factory'        : 'addLink18'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'link18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'link_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )

InitializeClass( Link18 )

# File Empty Sublass
from Products.CMFDefault import File

def addFile18( self
           , id
           , title=''
           , file=''
           , content_type=''
           , precondition=''
           , subject=()
           , description=''
           , contributors=()
           , effective_date=None
           , expiration_date=None
           , format='text/html'
           , language=''
           , rights=''):
    """
    Add a File
    """

    # cookId sets the id and title if they are not explicity specified
    id, title = OFS.Image.cookId(id, title, file)

    self=self.this()

    # Instantiate the object and set its description.
    fobj = File18( id, title, '', content_type, precondition, subject
               , description, contributors, effective_date, expiration_date
               , format, language, rights
               )

    # Add the File instance to self
    self._setObject(id, fobj)

    # 'Upload' the file.  This is done now rather than in the
    # constructor because the object is now in the ZODB and
    # can span ZODB objects.
    self._getOb(id).manage_upload(file)

class File18(File.File,Base18):
    meta_type = 'Base18 File'
    portal_type = 'File'
    isPortalContent = 1
    factory_type_information = ( { 'id'         : portal_type
                             , 'meta_type'      : meta_type
                             , 'description'    : """\
File objects can contain arbitrary downloadable files."""
                             , 'icon'           : 'file_icon.gif'
                             , 'product'        : 'Base18'
                             , 'factory'        : 'addFile18'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'file18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'download'
                                  , 'name'          : 'Download'
                                  , 'action'        : ''
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'file_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )
InitializeClass( File18 )

# Image Empty Sublass
from Products.CMFDefault import Image
import OFS.Image

def addImage18( self
            , id
            , title=''
            , file=''
            , content_type=''
            , precondition=''
            , subject=()
            , description=''
            , contributors=()
            , effective_date=None
            , expiration_date=None
            , format='image/png'
            , language=''
            , rights=''
            ):
    """
        Add an Image
    """

    # cookId sets the id and title if they are not explicity specified
    id, title = OFS.Image.cookId(id, title, file)

    self=self.this()

    # Instantiate the object and set its description.
    iobj = Image18( id, title, '', content_type, precondition, subject
                , description, contributors, effective_date, expiration_date
                , format, language, rights
                )

    # Add the Image instance to self
    self._setObject(id, iobj)

    # 'Upload' the image.  This is done now rather than in the
    # constructor because it's faster (see File.py.)
    self._getOb(id).manage_upload(file)

class Image18(Image.Image, Base18):
    meta_type = 'Base18 Image'
    portal_type = 'Image'
    isPortalContent = 1
    factory_type_information = ( { 'id'         : portal_type
                                 , 'meta_type'      : meta_type
                                 , 'description'    : """\
Image objects can be embedded in Portal documents."""
                                 , 'icon'           : 'image_icon.gif'
                                 , 'product'        : 'Base18'
                                 , 'factory'        : 'addImage18'
                                 , 'immediate_view' : 'metadata_edit_form'
                                 , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'image18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'image_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )
InitializeClass( Image18 )

# Folder Empty Sublass
from Products.CMFDefault import SkinnedFolder

def addSkinnedFolder18( self, id, title='', description='', REQUEST=None ):
    """
    """
    sf = SkinnedFolder18( id, title )
    sf.description = description
    self._setObject( id, sf )
    sf = self._getOb( id )
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

class SkinnedFolder18(SkinnedFolder.SkinnedFolder,Base18):
    meta_type = 'Base18 Folder'
    portal_type = 'Folder'
    isPortalContent = 1
    factory_type_information = ( { 'id'         : portal_type
                                 , 'meta_type'      : meta_type
                                 , 'description'    : """\
Skinned folders can define custom 'view' actions."""
                                 , 'icon'           : 'folder_icon.gif'
                                 , 'product'        : 'Base18'
                                 , 'factory'        : 'addSkinnedFolder18'
                                 , 'filter_content_types' : 0
                                 , 'immediate_view' : 'folder_edit_form'
                                 , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'folder18_view'
                                  , 'permissions'   :
                                     (CMFCorePermissions.View,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'folder_edit_form'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'localroles'
                                  , 'name'          : 'Local Roles'
                                  , 'action'        : 'folder_localrole_form'
                                  , 'permissions'   : \
                                        (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'syndication'
                                  , 'name'          : 'Syndication'
                                  , 'action'        : 'synPropertiesForm'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ManageProperties,)
                                  , 'category'      : 'folder'
                                  }
                                , { 'id'            : 'foldercontents'
                                  , 'name'          : 'Folder contents'
                                  , 'action'        : 'folder_contents'
                                  , 'permissions'   :
                                     (CMFCorePermissions.ListFolderContents,)
                                  , 'category'      : 'folder'
                                  }
                                )
                             }
                           ,
                           )
InitializeClass( SkinnedFolder18 )

# DiscussionItem Empty Sublass
from Products.CMFDefault import DiscussionItem

def addDiscussionItem18(self, id, title, description, text_format, text,
                      reply_to, RESPONSE=None):
    """
    Add a discussion item

    'title' is also used as the subject header
    if 'description' is blank, it is filled with the contents of 'title'
    'reply_to' is the object (or path to the object) which this is a reply to

    Otherwise, same as addDocument
    """

    if not description: description = title

    item = DiscussionItem( id )
    item.title = title
    item.description = description
    item.text_format = text_format
    item.text = text
    item.setReplyTo(reply_to)

    item._parse()
    self._setObject(id, item)

    if RESPONSE is not None:
        RESPONSE.redirect(self.absolute_url())

class DiscussionItem18(Document18, DiscussionItem.DiscussionItem):
    meta_type = 'Base18 Discussion Item'
    portal_type = 'Discussion Item'
    isPortalContent = 1
    factory_type_information = ( { 'id'         : portal_type
                                 , 'meta_type'      : meta_type
                             , 'description'    : """\
Discussion Items are documents which reply to other content.\
They should *not* be addable through the standard 'folder_factories'\
interface."""
                             , 'icon'           : 'discussionitem_icon.gif'
                             , 'product'        : '' # leave blank to suppress
                             , 'factory'        : ''
                             , 'immediate_view' : ''
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'discussionitem18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                ,
                                )
                             }
                           ,
                           )
InitializeClass( DiscussionItem18 )

class DiscussionItem18Container(DiscussionItem.DiscussionItemContainer):
    pass

# Favorite Empty Sublass
from Products.CMFDefault import Favorite

def addFavorite18(self, id, title='', remote_url='', description=''):
    """
    Add a Favorite
    """
    portal_url = getToolByName(self, 'portal_url')
    portal_obj = portal_url.getPortalObject()
    content_obj = portal_obj.restrictedTraverse( remote_url )
    relUrl = portal_url.getRelativeUrl( content_obj )
    o=Favorite18( id, title, relUrl, description )
    self._setObject(id,o)

class Favorite18(Favorite.Favorite,Base18):
    meta_type = 'Base18 Favorite'
    portal_type = 'Favorite'
    isPortalContent = 1
    factory_type_information = ( { 'id'         : portal_type
                                 , 'meta_type'      : meta_type
                             , 'description'    : """\
A Favorite is a Link to an intra-portal resource."""
                             , 'icon'           : 'link_icon.gif'
                             , 'product'        : 'Base18'
                             , 'factory'        : 'addFavorite18'
                             , 'immediate_view' : 'metadata_edit_form'
                             , 'actions'        :
                                ( { 'id'            : 'view'
                                  , 'name'          : 'View'
                                  , 'action'        : 'favorite18_view'
                                  , 'permissions'   : (
                                      CMFCorePermissions.View, )
                                  }
                                , { 'id'            : 'edit'
                                  , 'name'          : 'Edit'
                                  , 'action'        : 'link_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                , { 'id'            : 'metadata'
                                  , 'name'          : 'Metadata'
                                  , 'action'        : 'metadata_edit_form'
                                  , 'permissions'   : (
                                      CMFCorePermissions.ModifyPortalContent, )
                                  }
                                )
                             }
                           ,
                           )
InitializeClass( Favorite18 )

