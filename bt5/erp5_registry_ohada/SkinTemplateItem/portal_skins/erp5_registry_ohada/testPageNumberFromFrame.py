content_information = context.getContentInformation()
number_of_pages = int(content_information.get('Pages', 1))
max = number_of_pages - 1
page_list=range(number_of_pages)
result=[]
for i in page_list:
  result.append(context)
result[0].setFrame(0)
result[1].setFrame(1)
result[2].setFrame(2)
return result[0].getFrame()
