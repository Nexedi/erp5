##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id,update_method

# This script is only used in order to add a third button on
# dialog pages wich is only used for udpates

dialog_method = update_method
return context.base_dialog(form_id,cancel_url,dialog_method,selection_name,dialog_id,enable_cookie=1)
