## Script (Python) "SaleInvoice_printPdf"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=user_name='rc',printer='Xerox_DC_440',selection_name=None,render_id=None,template_id=None,number_copies=1,**kw
##title=
##
# generate a pdf file from the sale invoice

invoice = context
invoice_description = "Identifiant facture "+invoice.getId()

try:
  # generate the pdf
  pdf = invoice.Invoice_print_romain(batch_mode=1)
except:
  context.Coramy_sendMailToUser(user_name=user_name,mSubj="Génération d un pdf échouée",mMsg=invoice_description)
else:
  try:
    # Send it to a printer.
    invoice.sendRawToCups(printer, pdf, number_copies=number_copies)
  except:
    context.Coramy_sendMailToUser(user_name=user_name,mSubj="Impression d une facture vente échouée",mMsg=invoice_description)
