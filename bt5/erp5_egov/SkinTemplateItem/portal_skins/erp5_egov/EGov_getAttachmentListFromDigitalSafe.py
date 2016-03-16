'''
  Return a list of user documents corresponding to the title
'''


user_corresponding_document_list = []

# here we must search in the user digital safe documents that have the given title
#XXX to be done

if not len(user_corresponding_document_list):
  user_corresponding_document_list.append('Your digital safe contains no relevant document')
else:
  user_corresponding_document_list.append('Other')

return user_corresponding_document_list
