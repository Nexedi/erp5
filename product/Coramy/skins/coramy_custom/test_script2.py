## Script (Python) "test_script2"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
object_list = context.object_action_list(selection_name='purchase_packing_list_selection')

for object in object_list :
  object.deliver()
  object.invoice()

return 'fait', len(object_list)
