content_information = context.getContentInformation()
page_number = int(content_information.get('Pages', 0))
result=[]
page_list=range(page_number)
for i in page_list:
   result.append(context)
for i in result:
  for j in page_list:
    i.setFrame(j)
return i.getFrame()
