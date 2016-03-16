# we must keep parameters in sync with
# AccountingTransactionModule_setGroupingReference we cannot use **kw, because
# of ZPublisher introspection that pass automatically only named parameters

return context.AccountingTransactionModule_setGroupingReference(
                        uids=uids,
                        listbox=listbox,
                        listbox_uid=listbox_uid,
                        list_selection_name=list_selection_name,
                        node=node,
                        mirror_section=mirror_section,
                        update=1)
