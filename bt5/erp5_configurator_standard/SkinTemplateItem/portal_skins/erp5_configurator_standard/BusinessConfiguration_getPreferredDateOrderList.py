Base_translateString = context.Base_translateString

date_order_list = [
  ('', ''),
  (Base_translateString('Year / Month / Day'), 'ymd'),
  (Base_translateString('Day / Month / Year'), 'dmy'),
  (Base_translateString('Month / Day / Year'), 'mdy'),
  ]

return date_order_list
