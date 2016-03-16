# CashContainer_fastInputForm

portal = context.getPortalObject()
stool = portal.portal_selections

selected_uids = [x.getAggregateUid() for x in context.objectValues(
    portal_type="Monetary Issue Container")
]

selection_name = "%s_cash_container_selection" % (context.getPortalType(), )
context.REQUEST.other['list_selection_name'] = selection_name

stool.uncheckAll(selection_name)
stool.setSelectionToIds(
  selection_name=selection_name,
  selection_uids=selected_uids,
)
context.REQUEST.form['list_start'] = 0
return context.CashContainer_fastInputForm()
