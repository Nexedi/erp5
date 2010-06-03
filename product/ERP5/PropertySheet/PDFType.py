##############################################################################
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
#                     Mayoro DIAGNE <mayoro@nexedi.com>
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

class PDFType:
    """
      EXPERIMENTAL - DO NOT USE THIS PROPERTYSHEET BESIDES R&D
      PDFType properties for all Type definitions
    """

    _properties = (
      { 'id'                       : 'pdf_form'
      , 'storage_id'               : 'default_pdf_form'
      , 'description'              : 'A Scribus Form rendered as PDF'
      , 'type'                     : 'content'
      , 'portal_type'              : ( 'PDF', )
      , 'acquired_property_id'      : ('file', 'path', 'absolute_url',
                                     'width', 'height')
      , 'acquisition_base_category' : ()
      , 'acquisition_portal_type'   : ()
      , 'acquisition_copy_value'    : 0
      , 'acquisition_mask_value'    : 1
      , 'acquisition_sync_value'    : 0
      , 'acquisition_accessor_id'   : 'getDefaultPdfFormValue'
      , 'acquisition_depends'       : None
      , 'mode'        : 'w' },
      { 'id'                       : 'scribus_form'
      , 'storage_id'               : 'default_scribus_form'
      , 'description'              : 'A Scribus Form in native format'
      , 'type'                     : 'content'
      , 'portal_type'              : ( 'File', )
      , 'acquired_property_id'     : ( 'file', )
      , 'acquisition_base_category' : ()
      , 'acquisition_portal_type'   : ()
      , 'acquisition_copy_value'    : 0
      , 'acquisition_mask_value'    : 1
      , 'acquisition_sync_value'    : 0
      , 'acquisition_accessor_id'   : 'getDefaultScribusFormValue'
      , 'acquisition_depends'       : None
      , 'mode'        : 'w' },
      { 'id'                        : 'resolution'
      , 'description'               : 'Resolution of converted background from pdf file'
      , 'type'                      : 'int'
      , 'mode'                      : 'w' },
    )
