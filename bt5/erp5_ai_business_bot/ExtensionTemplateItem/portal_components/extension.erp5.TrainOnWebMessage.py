def WebMessage_trainOnWebMessage(self, language_arrays, tag_arrays, stopwords_arrays):
  message_tags = self.getSubjectList()
  if message_tags == []:
    return (language_arrays, tag_arrays)

  # clean up header from contact form, if there is one
  text = self.getTextContent()
  if text is None:
    return (language_arrays, tag_arrays)
  line_array = [line for line in text.splitlines() if line.strip() != '']
  if line_array[0][:6] == "  Name":
    line_array = line_array[4:]
    line_array[0] = line_array[0][14:]
  text = ' '.join(line_array)

  # determine message language
  message_language = "en"
  languages = language_arrays.keys()
  for language in languages:
    if language in message_tags:
      message_language = language
      message_tags.remove(language)

  # clean up text for training
  import string
  exclude = set(string.punctuation)
  text = text.lower()
  text = ''.join(ch for ch in text if ch not in exclude)
  text = [w for w in text if w not in stopwords_arrays[message_language]]

  # add text into language_arrays and tag_arrays
  for word in text:
    language_arrays[message_language][word] = language_arrays[message_language].get(word, 1) + 1

  tag_array = tag_arrays[message_language]
  tags = tag_array.keys()
  for word in text:
    for t in range(len(message_tags)):
      if message_tags[t] in tags:
        tag_array[message_tags[t]][word] = tag_array[message_tags[t]].get(word, 1) + 1
      else:
        tag_array[message_tags[t]] = {}
        tag_array[message_tags[t]][word] = 1

  tag_arrays[message_language] = tag_array
  return (language_arrays, tag_arrays)