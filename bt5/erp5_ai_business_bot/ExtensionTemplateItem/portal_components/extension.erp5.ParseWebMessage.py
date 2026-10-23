def WebMessage_parseWebMessage(self):
  '''
  This function automatically determines the keywords/subject/tags of a message
  in order to follow up on it
  '''
  import pickle
  message = self.getObject()
  portal=self.getPortalObject()
  people = portal.person_module
  text_content = message.getTextContent()
  if text_content is None:
    return()
  suggested_subject_list = []
  sender_info=False

  # process header and create person for response
  line_array = [line for line in text_content.splitlines() if line.strip() != '']
  if line_array[0][:14] == "<p>&nbsp; Name":
    sender_info=True
    line_array[:4] = [line.split(':')[1][:-4] for line in line_array[:4]]
    name = line_array[0]
    email = line_array[2][1:]
    line_array = line_array[4:]
    line_array[0] = line_array[0].split(':')[1]
    
    new_id = str(people.generateNewId())
    self.portal_types.constructContent(
        type_name="Person",
        container=people,
        id=new_id
    )
    person = people[new_id]
    (first_name, last_name) = (name.split()[0], name.split()[1])
    person.edit(first_name=first_name, last_name=last_name)
    person.setEmailText(email)
    message.setSource("person_module/" + new_id)

  text = ' '.join(line_array)

  # get model from file
  kw = dict(portal_type = 'File', \
            reference='ai_business_bot',
            title="AI Business Bot")
  erp5_file = portal.portal_catalog.getResultValue(**kw)
  if not erp5_file:
    return "No model found to be applied to this Web Message.  Run Set Web Message Model in Event Module first."
  model_as_string = erp5_file.getData()
  model = pickle.loads(model_as_string)
  language_arrays = model[0]
  tag_arrays = model[1]
  stopwords_arrays = model[2]

  # determine language of message
  message_language = "en"
  languages = language_arrays.keys()
  language_relevance = {languages[i]:0 for i in range(len(languages))}
  for word in text_content:
    for language in languages:
      if word in language_arrays[language]:
        word_relevance = (language_arrays[language][word])/(list(language_arrays[language].values())[0])
        language_relevance[language] = language_relevance[language] + word_relevance
  message_language = max(language_relevance, key=language_relevance.get)
  suggested_subject_list.append(message_language)

  # clean up text for analysis
  import string
  exclude = set(string.punctuation)
  text = text_content.lower()
  text = ''.join(ch for ch in text if ch not in exclude)
  text = [w for w in text if w not in stopwords_arrays[message_language]]

  # determine relevance of each tag to message
  tag_array = tag_arrays[message_language]
  tags = tag_array.keys()
  tag_relevance = {tags[i]:0 for i in range(len(tags))}
  for word in text:
    for t in range(len(tags)):
      if word in tag_array[tags[t]]:
        word_relevance = (tag_array[tags[t]][word]/list(tag_array[tags[t]].values())[0])
        tag_relevance[tags[t]] = tag_relevance[tags[t]] + word_relevance

  # apply tags
  average_relevance = sum(tag_relevance.values()) / float(len(tag_relevance.values()))
  for t in tag_relevance:
    if tag_relevance[t] >= average_relevance*2:
      suggested_subject_list.append(t)

  message.setSubjectList(suggested_subject_list)
  if sender_info:
    return self.WebMessage_followUpWebMessage(tags=suggested_subject_list)
  else:
    return self.Base_redirect()