## Script (Python) "testseb"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery_list =context.object_action_list(selection_name='sales_packing_list_selection',max_nb=10)
return repr(delivery_list)
