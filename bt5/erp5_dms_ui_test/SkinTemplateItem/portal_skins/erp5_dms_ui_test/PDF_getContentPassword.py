# type: () -> str
if context.getId() == 'test_ERP5_Logo_Encrypted_PDF':
  return 'secret'
return context.skinSuper('erp5_dms_ui_test', 'PDF_getContentPassword')(REQUEST=REQUEST)
