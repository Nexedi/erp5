## Script (Python) "SalesOrder_reportByResource"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=source_section
##title=
##
request = context.REQUEST
cr = '\r'
tab = '\t'
report = 'Produit' + tab + 'Quantite' + tab + 'Prix total' + cr

source_section_item_list = source_section.split('.')
source_section_object = context.portal_categories.group
for source_item in source_section_item_list :
  source_section_object = source_section_object[source_item]

report_list = context.SalesOrder_zReportByResource(source_section_uid=source_section_object.getUid())

for report_item in report_list :
  report += report_item.resource_id + tab
  report += str(report_item.quantity).replace('.',',')  + tab
  report += str(report_item.total_price).replace('.',',') + cr

request.RESPONSE.setHeader('Content-Type','application/text')

return report
