## Script (Python) "asPDF"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Traveral helper to render report
##
request = context.REQUEST

if len(traverse_subpath) >= 2:
	templatename = traverse_subpath[0]
	documentname = traverse_subpath[1]
	if len(traverse_subpath) >= 3:
		resultname = traverse_subpath[2]
	else:
		resultname = context.id + '.pdf'
	
	report_tool = context.portal_report
	doc_txt = getattr(context,documentname,None)

	if doc_txt:
		doc_xml = context.testdocument_pdf(pdftemplate=templatename)
		pdf = report_tool.renderPDF(templatename,doc_xml)
		
		request.RESPONSE.setHeader('Content-Type','application/pdf')
		request.RESPONSE.setHeader('Content-Length',len(pdf))
		request.RESPONSE.setHeader('Content-Disposition','inline;filename=Myfile.pdf')

		return pdf

url = '%s/%s?%s' % (context.portal_url(),'index_html','portal_status_message=error+using+asPDF.')
return request.RESPONSE.redirect(url)
