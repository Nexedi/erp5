## Script (Python) "Base_createNewDocument"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
REQUEST=context.REQUEST

# Add an object of the same type as self
parent = context.aq_parent
# XXX May be this need to be changed in order to get something else than
# the permission "Add portal content"
new_id = parent.generateNewId()
context.portal_types.constructContent(type_name=context.portal_type,
                        container=parent,
                        id=str(new_id),
                        RESPONSE=REQUEST.RESPONSE)
# parent[new_id].flushActivity(invoke=1)
# parent.invokeFactory(type_name=context.portal_type,
#       id=str(parent.generateNewId()),
#        RESPONSE=REQUEST.RESPONSE)
#parent.portal_types.constructContent(type_name=context.portal_type,
#     container=context,
#     id=str(parent.generateNewId()),
#      RESPONSE=REQUEST.RESPONSE)

return REQUEST.RESPONSE
