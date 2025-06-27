from Products.ERP5Type.Utils import md5

attribute_list = [
  "title",
  "street_address",
  "address_extension",
  "zip_code",
  "city",
  "region",
  "int_index",
  "address_id_domain",
  "buyer_id",
  "buyer_location_id",
  "storage_location_id",
  "buyer_account_id",
  "physical_address_id",
]

return md5("".join([str(context.getProperty(x) or '') for x in attribute_list])).hexdigest()
