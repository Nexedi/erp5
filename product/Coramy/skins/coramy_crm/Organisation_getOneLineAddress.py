## Script (Python) "Organisation_getOneLineAddress"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
address = context.getDefaultAddress()
if address != None:
  zip_code = context.getDefaultAddress().getZipCode()
  city = context.getDefaultAddress().getCity()
else:
  zip_code = ''
  city = ''

region = context.getDefaultAddressRegion()
if region == None:
  region = ''
else:
  region = region.split('/')[-1]

return 'Lieu livraison : %s %s %s' % (zip_code, city, region)
