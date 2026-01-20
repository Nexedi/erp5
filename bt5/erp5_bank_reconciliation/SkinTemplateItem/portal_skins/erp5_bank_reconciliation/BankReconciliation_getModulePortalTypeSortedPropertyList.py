translateString = context.Base_translateString
# XXX: assumes we only allow one Portal Type for children
line_portal_type_reference = context.allowedContentTypes()[0].id

base_property_list = [
  ("Transaction Date", "start_date"),
  ("Accounting Date", "stop_date"),
  ("Title", "title"),
  ("Reference", "reference"),
  ("Debit", "source_debit"),
  ("Credit", "source_credit"),
]
base_property_list.sort()

return map(lambda x: (
  translateString(x[0]),
  "%s.%s" % (line_portal_type_reference, x[1]),
), base_property_list)
