portal = context.getPortalObject()
N_ = portal.Base_translateString

letter_post_list = context.searchFolder(simulation_state='export_prepared')

merged_pdf_content = portal.ERP5Site_mergePDFList((
   letter_post.getObject().getData() for letter_post in letter_post_list if letter_post.getData()))

for letter_post in letter_post_list:
  letter_post.activate(activity='SQLQueue').export(comment=comment)

with portal.Localizer.translationContext(localizer_language):
  result_pdf = portal.document_module.newContent(
    portal_type='PDF',
    title=N_('Printing of Letter Post'),
    data=merged_pdf_content,
    content_type='application/pdf',
    filename='letter_export.pdf',
  )

  result_pdf.release()

  portal.portal_notifications.activate(activity='SQLQueue').sendMessage(
    recipient=[user_name,],
    subject=N_('Letters to print'),
    message='Please, find the PDF aggregating all Letters to send here : %s' % result_pdf.getAbsoluteUrl(),
    message_text_format='text/plain',
    notifier_list=('Mail Message',),
    store_as_event=False,
  )
