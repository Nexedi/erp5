## Script (Python) "Folder_createModule"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=module_id='0', module_title='', module_type=''
##title=
##
request = context.REQUEST

module_title = module_title.replace('_',' ')
module_type = module_type.replace('_',' ')
context.portal_types.constructContent(type_name=module_type,
                        container = context,
                        title = module_title,
                        id = module_id)

redirect_url = '%s?%s' % ( context.absolute_url()+'/'+module_id
                              , 'portal_status_message=1+module+créé.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
