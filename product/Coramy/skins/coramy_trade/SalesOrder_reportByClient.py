## Script (Python) "SalesOrder_reportByClient"
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
report = 'Client' + 5*tab + 'Quantite' + tab + 'Prix total' + cr

source_section_item_list = source_section.split('.')
source_section_object = context.portal_categories.group
for source_item in source_section_item_list :
  source_section_object = source_section_object[source_item]

report_list = context.SalesOrder_zReportByClient(source_section_uid=source_section_object.getUid())

for report_item in report_list :
  if report_item.client is None :
    report += '' + 5*tab
  else :
    client_item_list = report_item.client.split('/')
    compteur = 0
    for client_item in client_item_list :
      report += client_item + tab
      compteur +=1
    for i in range(5-compteur) :
      report += tab
  report += str(report_item.quantity).replace('.',',')  + tab
  report += str(report_item.total_price).replace('.',',') + cr

request.RESPONSE.setHeader('Content-Type','application/text')

return report
