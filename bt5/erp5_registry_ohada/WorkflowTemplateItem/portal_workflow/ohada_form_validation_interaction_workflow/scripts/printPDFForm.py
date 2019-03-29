from Products.DCWorkflow.DCWorkflow import ValidationFailed
# This script is used to the automatic printing
# It is called after the validation of the registry officer
request_eform = state_change['object']
request = request_eform.REQUEST
response = request.RESPONSE
printer_name = request_eform.portal_preferences.getPreferredPrinterName()
form_pdf_portal_type = request_eform.getPortalType()
pdf_view_name = '%s_view%sAsPdf' % (form_pdf_portal_type, form_pdf_portal_type)
form_view_pdf = getattr(request_eform, pdf_view_name, None)
if form_view_pdf is None:
  raise ValidationFailed('PDF view %s not found' % pdf_view_name)

signed_pdf_name = context.addBackgroundOnPdfFile(form_view_pdf.generatePDF(),
                                                 getattr(context,'signature.pdf'))

context.printFile(printer_name = printer_name,
                  file_path_to_print = signed_pdf_name,
                  use_ps_file = True,
                  nb_copy = 4)

# print sub forms (as M0 Bis)
form_bis_result = request_eform.searchFolder(portal_type='%s Bis' % form_pdf_portal_type)
form_bis_list = [form.getObject() for form in form_bis_result]
for form_bis in form_bis_list:
  form_portal_type = form_bis.getPortalType().replace(' ', '')
  view_name = '%s_view%sAsPdf' % (form_portal_type, form_portal_type)
  form_pdf_view = getattr(form_bis, view_name, None)
  if form_pdf_view is None:
    raise ValidationFailed('PDF view %s not found' % form_pdf_view)
  form_bis_signed_pdf_name = context.addBackgroundOnPdfFile(form_pdf_view.generatePDF(),
                                                            getattr(context,'signature.pdf'))
  context.printFile(printer_name = printer_name,
                    file_path_to_print = signed_pdf_name,
                    use_ps_file = True,
                    nb_copy = 4)
