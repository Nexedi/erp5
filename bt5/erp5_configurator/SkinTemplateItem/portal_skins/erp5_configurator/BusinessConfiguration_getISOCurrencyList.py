from Products.ERP5Type.Cache import CachingMethod
result = []
if empty_first_element:
  result = [['', ''],]

filename = "standard_currency_list.ods"
rows = CachingMethod(context.ConfigurationTemplate_readOOCalcFile,
                      script.getId(),
                      cache_factory="erp5_content_long")(filename)

Base_translateString = context.Base_translateString
for row in rows:
  currency_title = Base_translateString(row['currency'])
  line = [currency_title, '%s;%s;%s' % (row['iso_code'].strip(),
                                        row['precision'].strip(),
                                        row['currency'].strip())]
  result.append(line)
return result
