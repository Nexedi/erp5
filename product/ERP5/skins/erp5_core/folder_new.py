REQUEST=context.REQUEST
content_types = context.allowedContentTypes()

# Add an object of the same type as the container 
# or if allowed content types is 1 add that type

if len(content_types) == 1:
  type_name = content_types[0].id
else:
  type_name = context.portal_type

new_id = context.generateNewId()
context.portal_types.constructContent(type_name=type_name,
                        container=context,
                        id=str(new_id),
                        RESPONSE=REQUEST.RESPONSE)
#context[new_id].flushActivity(invoke=1)

return REQUEST.RESPONSE
