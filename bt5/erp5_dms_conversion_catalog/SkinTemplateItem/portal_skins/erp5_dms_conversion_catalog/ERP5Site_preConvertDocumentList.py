"""
  When fired this script will do a pre conversion of all documents (including Images)
  in ERP5 instance.
  It will do that recursively in entire ERP5 instance.

"""
context.ERP5Site_checkDataWithScript("Base_callPreConvert",
                                     tag="pre_convert",
                                     packet=2,
                                     id_list=["document_module", "image_module", "web_page_module"])
print "OK"
return printed
