from json import dumps

gadget_list = context.portal_catalog(portal_type="Gadget")

gadget_data_list = []
for gadget in gadget_list:
  image_url = gadget.getRelativeUrl() + "/default_image?resolution=75.0&display=xsmall&format=png"
  gadget_data_list.append(dict(title=gadget.getTitle(),
                               image_url=image_url,
                               id=gadget.getId()))
  
return dumps(gadget_data_list)
