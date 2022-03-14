# this script allow to create a new object from this current one

from builtins import str
current_object = context.getObject()
module = context.getPortalObject().support_request_module

# Create a new object
new_id = str(module.generateNewId())
context.portal_types.constructContent(type_name='Support Request',
        container=module,
        id=new_id
)
new_object = module[new_id]


# If we do this before, each added line will take 20 times more time
# because of programmable acquisition
new_object.edit(
        title=current_object.getTitle(),
        causality_value=context,
        client_value_list = current_object.getSourceValueList()
)
# Now create the relation between the current object and the new one
current_object.setFollowUpValueList([new_object])
