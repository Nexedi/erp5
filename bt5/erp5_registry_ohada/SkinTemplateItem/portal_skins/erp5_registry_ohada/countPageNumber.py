content_information = context.getContentInformation()
page_number = int(content_information.get('Pages', 0))
page_number =page_number-1
return page_number
