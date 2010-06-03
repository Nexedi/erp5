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
