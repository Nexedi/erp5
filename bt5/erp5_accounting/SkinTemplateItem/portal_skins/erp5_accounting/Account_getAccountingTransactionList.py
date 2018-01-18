"""Returns Accounting Transactions where this account is node.
"""
kw.update(dict(
  node_uid=context.getUid(), # this line is the reason for this whole script

  # the rest is here to specify explicitely script's parameters and pass them through transparently
  selection_name=selection_name,
  omit_grouping_reference=omit_grouping_reference,
  analytic_column_list=analytic_column_list,
  node_category=node_category,
  node_category_strict_membership=node_category_strict_membership,
  mirror_section_category=mirror_section_category,
  # from_date=from_date, # if added from_date terrible things start to happen
))
return context.Node_getAccountingTransactionList(**kw)
