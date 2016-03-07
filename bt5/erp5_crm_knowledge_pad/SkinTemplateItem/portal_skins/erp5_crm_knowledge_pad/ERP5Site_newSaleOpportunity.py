from DateTime import DateTime
portal = context.getPortalObject()
form = context.REQUEST.form

# XXX this form has to be validated !!!!!
saletitle = context.REQUEST.get('field_your_sale_title')
clientname = context.REQUEST.get('field_your_client_name')

portal = context.getPortalObject()

client = None
if clientname:
  client = portal.portal_catalog.getResultValue(title=clientname, portal_type=('Person', 'Organisation'))
description = context.REQUEST.get('field_your_description')
quantity = context.REQUEST.get('field_your_quantity')
price = context.REQUEST.get('field_your_price')
stopdate_day = context.REQUEST.get('subfield_field_your_stop_date_day')
stopdate_month = context.REQUEST.get('subfield_field_your_stop_date_month')
stopdate_year = context.REQUEST.get('subfield_field_your_stop_date_year')
stopdate = DateTime("%s/%s/%s" %(stopdate_year, stopdate_month, stopdate_day))

sale_opportunity = portal.sale_opportunity_module.newContent(portal_type="Sale Opportunity")
sale_opportunity.setTitle(saletitle)
sale_opportunity.setDestinationSectionValue(client)
sale_opportunity.setDescription(description)
sale_opportunity.setQuantity(quantity)
sale_opportunity.setPrice(price)
sale_opportunity.setStopDate(stopdate)

message = 'New Sale Opportunity created.'
if clientname and client is None:
  message = 'New Sale Opportunity created, but client not found.'
return sale_opportunity.Base_redirect("", keep_items=dict(portal_status_message=message))
