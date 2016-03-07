message_list = []

for m in context.getDivergenceList():
  message_list.append(str(m.getTranslatedMessage()))
return ', '.join(message_list)
