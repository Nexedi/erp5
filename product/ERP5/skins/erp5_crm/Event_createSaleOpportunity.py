## Script (Python) "Event_createSaleOpportunity"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# this script allow to create a new object from this current one

current_object = context.getObject()
module = context.getPortalObject().opportunity

# Create a new object
new_id = str(module.generateNewId())
context.portal_types.constructContent(type_name='Sale Opportunity',
        container=module,
        id=new_id
)
new_object = module[new_id]


# If we do this before, each added line will take 20 times more time
# because of programmable acquisition
new_object.edit(
        title=current_object.getTitle(),
        client_value_list = current_object.getSourceValueList()
)
# Now create the relation between the current object and the new one
current_object.setFollowUpValueList([new_object])
