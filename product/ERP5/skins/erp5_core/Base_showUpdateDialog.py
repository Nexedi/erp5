## Script (Python) "Base_showUpdateDialog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id,update_method
##title=
##
# This script is only used in order to add a third button on
# dialog pages wich is only used for udpates

dialog_method = update_method
return context.Base_callDialogMethod(form_id,cancel_url,dialog_method,selection_name,dialog_id,enable_pickle=1)
