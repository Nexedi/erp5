child_raw_text = ""

child_brain_list = context.DiscussionThread_getContextPostList()
for child in child_brain_list:
  child_raw_text += child.asRawText()
#XX If word is last, it is not displayed
return child_raw_text
