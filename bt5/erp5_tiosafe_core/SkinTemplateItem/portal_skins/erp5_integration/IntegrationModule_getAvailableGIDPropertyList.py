"""
This script returns the list of property that can be used
to configure the GID for a given portal type
"""
property_list = ()
if "person_module" in context.getId():
  property_list = (('First Name','firstname'),
                  ('Last Name','lastname'),
                  ('Birthday','birthday'),
                  ('Email','email'))


elif context.getId() == "product_module":
  property_list = (('Title','title'),
                  ('Reference','reference'),
                  ('Ean13','ean13'),('ID','id'))


elif context.getId() == "sale_order_module":
  property_list = (('Reference','reference'),)


elif "organisation_module" in context.getId():
  property_list = (('Title','title'),
                  ('Country','country'),
                  ('Email','email'))

elif "payment_transaction_module" in context.getId():
  property_list = (('Title','title'),
                  ('Reference','reference'),('ID','id'))

return property_list
