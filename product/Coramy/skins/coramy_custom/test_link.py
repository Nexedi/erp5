## Script (Python) "test_link"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST

transformation_list = context.transformation_sql_search(modele_id = context.id)

if len(transformation_list) > 0:
  jump_url = transformation_list[0].absolute_url()
else:
  jump_url = context.absolute_url()

return request[ 'RESPONSE' ].redirect( '%s/view' % jump_url )
