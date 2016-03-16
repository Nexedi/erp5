content_information = context.getContentInformation()
page_number = int(content_information.get('Pages', 0))
return [[page_number]]
