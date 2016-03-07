REQUEST = context.REQUEST
message = context.CheckbookReception_importItemFile(import_file=import_file, REQUEST=REQUEST, **kw)
redirect_url = '%s/view?%s' % ( context.absolute_url()
                                , 'portal_status_message=%s' % message
                                )
request = context.REQUEST
request[ 'RESPONSE' ].redirect( redirect_url )
