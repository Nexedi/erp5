content_information = context.getContentInformation()
page_number = int(content_information.get('Pages', 0))
page_list=range(page_number)
frame=[]
for i in page_list:
   frame.append(i)
return frame
