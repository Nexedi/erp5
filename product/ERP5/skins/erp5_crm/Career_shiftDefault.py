## Script (Python) "Career_shiftDefault"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
object_list = []
default_career = None
new_start_date = None

# Create a list of all career line except the default one
for object in context.objectValues():
    if object.getPortalType() == 'Career':
        if object.getId() != 'default_career':    
            object_list += [object]
        else:
            default_career = object
            new_start_date = default_career.getStopDate()

# No default career
if default_career == None:
    return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/person_career_view' + '?portal_status_message=Current+career+need+to+be+defined')

# Inverse sort of the list by id
object_list.sort(lambda x, y: -cmp(int(x.getId()), int(y.getId())))

# Shift all career lines id values
new_id = str(context.generateNewId())
for career_line in object_list:
    current_id = career_line.getId()
    context.manage_renameObject(current_id, new_id)
    new_id = current_id

# Create a new default_career
context.manage_renameObject('default_career', new_id)
new_default = context.manage_copyObjects(ids=(new_id,))
new_object = context.manage_pasteObjects(new_default)
context.manage_renameObject(new_object[0]['new_id'], 'default_career')
context.setDefaultCareerStopDate(None)
context.setDefaultCareerStartDate(new_start_date)

return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/person_career_view' + '?portal_status_message=New+career+step+added')
