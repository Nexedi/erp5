## Script (Python) "Variated_getColorisList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
coloris_list = context.getColorisList()
coloris_coramy = []
coloris_client = []
for coloris in coloris_list :
  coloris_items = coloris.split('/')
  coloris_coramy.append(coloris_items[len(coloris_items)-1])

  try :
    coloris_object = context.restrictedTraverse('/'.join(coloris_items[0:len(coloris_items)]))
  except :
    coloris_object = None

  if coloris_object is not None :
    if not coloris_object.getDestinationReference() in (None,'',' ') :
      coloris_client.append(coloris_object.getDestinationReference())
    else :
      coloris_client.append(coloris_items[len(coloris_items)-1])
  else :
    coloris_client.append(coloris_items[len(coloris_items)-1])

coloris = [coloris_coramy, coloris_client, coloris_list]
return coloris
