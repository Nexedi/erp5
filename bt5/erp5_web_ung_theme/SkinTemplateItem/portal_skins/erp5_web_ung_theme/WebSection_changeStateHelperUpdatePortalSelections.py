# prevent lose of checked itens at listbox after click to print
# Do what Base_updateListboxSelection does, overwriting listbox_uid

import ipdb
ipdb.set_trace()

selection_name = context.REQUEST.get('list_selection_name', None)
listbox_uid = context.REQUEST.get('knowledge_pad_module_ung_knowledge_pad_ung_docs_listbox_content_listbox_uid', None)
uids = context.REQUEST.get('uids', None)
context.portal_selections.updateSelectionCheckedUidList(listbox_uid = listbox_uid,
                                                        uids=uids,
                                                        selection_name=selection_name,
                                                        REQUEST=context.REQUEST)

gadget_form_id = context.REQUEST.get('gadget_form_id', 'erp5_web_ung_content_layout')
keep_items=dict(
    form_id=gadget_form_id,
    selection_name=selection_name)


#return context.ERP5Site_redirect('Folder_viewWorkflowActionDialog', keep_items=keep_items, **kw)
#return context, context.REQUEST, context.REQUEST.form, context.REQUEST.get('list_selection_name', None), kw
