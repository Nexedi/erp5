if not active_process_url:
  return context.Base_renderForm('Base_viewUploadDocumentFromCameraStep1Dialog',
                                  message='Please capture one document at least')

return context.Base_renderForm('Base_viewUploadDocumentFromCameraStep2Dialog',
                               message='Please fill the information')
