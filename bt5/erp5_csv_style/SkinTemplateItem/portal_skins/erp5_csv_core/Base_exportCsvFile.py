request  = context.REQUEST

from ZTUtils import make_query
kw = { 'portal_skin' : 'CSV',
       'export_only' : export_only }

redirect_url = '%s?%s' % ( context.absolute_url()+'/'+form_id,
                             make_query(kw) )

return request[ 'RESPONSE' ].redirect( redirect_url )
