"""
This script returns the list of property that can be used
to configure the GID for a given portal type
"""
property_list = ()
if portal_type == "Person":
  property_list = (('First Name','firstname'),
                  ('Last Name','lastname'),
                  ('Birthday','birthday'),
                  ('Email','email'))


if portal_type == "Product":
  property_list = (('Title','title'),
                  ('Reference','reference'),
                  ('Ean13','ean13'),)


if portal_type == "Sale Order":
  property_list = (('Reference','reference'),)


return property_list
