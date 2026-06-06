def WebMessage_testModel(self):
  """ 
  Test the accuracy of the web message model
  """

  from Products.ZSQLCatalog.SQLCatalog import Query
  from Products.ZSQLCatalog.SQLCatalog import NegatedQuery
  import datetime
  import time
  import random

  # instantiate arrays
  stopwords_arrays = {}
  stopwords_arrays["en"] = ['p', 'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours\tourselves', 'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
  stopwords_arrays["fr"] = ['p', 'alors', 'au', 'aucuns', 'aussi', 'autre', 'avant', 'avec', 'avoir', 'bon', 'car', 'ce', 'cela', 'ces', 'ceux', 'chaque', 'ci', 'comme', 'comment', 'dans', 'des', 'du', 'dedans', 'dehors', 'depuis', 'devrait', 'doit', 'donc', 'dos', 'd\xc3\xa9but', 'elle', 'elles', 'en', 'encore', 'essai', 'est', 'et', 'eu', 'fait', 'faites', 'fois', 'font', 'hors', 'ici', 'il', 'ils', 'je', 'juste', 'la', 'le', 'les', 'leur', 'l\xc3\xa0', 'ma', 'maintenant', 'mais', 'mes', 'mine', 'moins', 'mon', 'mot', 'm\xc3\xaame', 'ni', 'nomm\xc3\xa9s', 'notre', 'nous', 'ou', 'o\xc3\xb9', 'par', 'parce', 'pas', 'peut', 'peu', 'plupart', 'pour', 'pourquoi', 'quand', 'que', 'quel', 'quelle', 'quelles', 'quels', 'qui', 'sa', 'sans', 'ses', 'seulement', 'si', 'sien', 'son', 'sont', 'sous', 'soyez', 'sujet', 'sur', 'ta', 'tandis', 'tellement', 'tels', 'tes', 'ton', 'tous', 'tout', 'trop', 'tr\xc3\xa8s', 'tu', 'voient', 'vont', 'votre', 'vous', 'vu', '\xc3\xa7a', '\xc3\xa9taient', '\xc3\xa9tat', '\xc3\xa9tions', '\xc3\xa9t\xc3\xa9', '\xc3\xaatre']
  stopwords_arrays["pt"] = ['p', 'a', 'ainda', 'alem', 'ambas', 'ambos', 'antes', 'ao', 'aonde', 'aos', 'apos', 'aquele', 'aqueles', 'as', 'assim', 'com', 'como', 'contra', 'contudo', 'cuja', 'cujas', 'cujo', 'cujos', 'da', 'das', 'de', 'dela', 'dele', 'deles', 'demais', 'depois', 'desde', 'desta', 'deste', 'dispoe', 'dispoem', 'diversa', 'diversas', 'diversos', 'do', 'dos', 'durante', 'e', 'ela', 'elas', 'ele', 'eles', 'em', 'entao', 'entre', 'essa', 'essas', 'esse', 'esses', 'esta', 'estas', 'este', 'estes', 'ha', 'isso', 'isto', 'logo', 'mais', 'mas', 'mediante', 'menos', 'mesma', 'mesmas', 'mesmo', 'mesmos', 'na', 'nas', 'nao', 'nas', 'nem', 'nesse', 'neste', 'nos', 'o', 'os', 'ou', 'outra', 'outras', 'outro', 'outros', 'pelas', 'pelas', 'pelo', 'pelos', 'perante', 'pois', 'por', 'porque', 'portanto', 'proprio', 'propios', 'quais', 'qual', 'qualquer', 'quando', 'quanto', 'que', 'quem', 'quer', 'se', 'seja', 'sem', 'sendo', 'seu', 'seus', 'sob', 'sobre', 'sua', 'suas', 'tal', 'tambem', 'teu', 'teus', 'toda', 'todas', 'todo', 'todos', 'tua', 'tuas', 'tudo', 'um', 'uma', 'umas', 'uns']
  stopwords_arrays["ja"] = ['p', '\xe3\x81\x93\xe3\x82\x8c', '\xe3\x81\x9d\xe3\x82\x8c', '\xe3\x81\x82\xe3\x82\x8c', '\xe3\x81\x93\xe3\x81\xae', '\xe3\x81\x9d\xe3\x81\xae', '\xe3\x81\x82\xe3\x81\xae', '\xe3\x81\x93\xe3\x81\x93', '\xe3\x81\x9d\xe3\x81\x93', '\xe3\x81\x82\xe3\x81\x9d\xe3\x81\x93', '\xe3\x81\x93\xe3\x81\xa1\xe3\x82\x89', '\xe3\x81\xa9\xe3\x81\x93', '\xe3\x81\xa0\xe3\x82\x8c', '\xe3\x81\xaa\xe3\x81\xab', '\xe3\x81\xaa\xe3\x82\x93', '\xe4\xbd\x95', '\xe7\xa7\x81', '\xe8\xb2\xb4\xe6\x96\xb9', '\xe8\xb2\xb4\xe6\x96\xb9\xe6\x96\xb9', '\xe6\x88\x91\xe3\x80\x85', '\xe7\xa7\x81\xe9\x81\x94', '\xe3\x81\x82\xe3\x81\xae\xe4\xba\xba', '\xe3\x81\x82\xe3\x81\xae\xe3\x81\x8b\xe3\x81\x9f', '\xe5\xbd\xbc\xe5\xa5\xb3', '\xe5\xbd\xbc', '\xe3\x81\xa7\xe3\x81\x99', '\xe3\x81\x82\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x99', '\xe3\x81\x8a\xe3\x82\x8a\xe3\x81\xbe\xe3\x81\x99', '\xe3\x81\x84\xe3\x81\xbe\xe3\x81\x99', '\xe3\x81\xaf', '\xe3\x81\x8c', '\xe3\x81\xae', '\xe3\x81\xab', '\xe3\x82\x92', '\xe3\x81\xa7', '\xe3\x81\x88', '\xe3\x81\x8b\xe3\x82\x89', '\xe3\x81\xbe\xe3\x81\xa7', '\xe3\x82\x88\xe3\x82\x8a', '\xe3\x82\x82', '\xe3\x81\xa9\xe3\x81\xae', '\xe3\x81\xa8', '\xe3\x81\x97', '\xe3\x81\x9d\xe3\x82\x8c\xe3\x81\xa7', '\xe3\x81\x97\xe3\x81\x8b\xe3\x81\x97']
  stopwords_arrays["es"] = ['p', 'un', 'una', 'unas', 'unos', 'uno', 'sobre', 'todo', 'tambi\xc3\xa9n', 'tras', 'otro', 'alg\xc3\xban', 'alguno', 'alguna', 'algunos', 'algunas', 'ser', 'es', 'soy', 'eres', 'somos', 'sois', 'estoy', 'esta', 'estamos', 'estais', 'estan', 'como', 'en', 'para', 'atras', 'porque', 'por', 'qu\xc3\xa9', 'estado', 'estaba', 'ante', 'antes', 'siendo', 'ambos', 'pero', 'por', 'poder', 'puede', 'puedo', 'podemos', 'podeis', 'pueden', 'fui', 'fue', 'fuimos', 'fueron', 'hacer', 'hago', 'hace', 'hacemos', 'haceis', 'hacen', 'cada', 'fin', 'incluso', 'primero', 'desde', 'conseguir', 'consigo', 'consigue', 'consigues', 'conseguimos', 'consiguen', 'ir', 'voy', 'va', 'vamos', 'vais', 'van', 'vaya', 'gueno', 'ha', 'tener', 'tengo', 'tiene', 'tenemos', 'teneis', 'tienen', 'el', 'la', 'lo', 'las', 'los', 'su', 'aqui', 'mio', 'tuyo', 'ellos', 'ellas', 'nos', 'nosotros', 'vosotros', 'vosotras', 'si', 'dentro', 'solo', 'solamente', 'saber', 'sabes', 'sabe', 'sabemos', 'sabeis', 'saben', 'ultimo', 'largo', 'bastante', 'haces', 'muchos', 'aquellos', 'aquellas', 'sus', 'entonces', 'tiempo', 'verdad', 'verdadero', 'verdadera', 'cierto', 'ciertos', 'cierta', 'ciertas', 'intentar', 'intento', 'intenta', 'intentas', 'intentamos', 'intentais', 'intentan', 'dos', 'bajo', 'arriba', 'encima', 'usar', 'uso', 'usas', 'usa', 'usamos', 'usais', 'usan', 'emplear', 'empleo', 'empleas', 'emplean', 'ampleamos', 'empleais', 'valor', 'muy', 'era', 'eras', 'eramos', 'eran', 'modo', 'bien', 'cual', 'cuando', 'donde', 'mientras', 'quien', 'con', 'entre', 'sin', 'trabajo', 'trabajar', 'trabajas', 'trabaja', 'trabajamos', 'trabajais', 'trabajan', 'podria', 'podrias', 'podriamos', 'podrian', 'podriais', 'yo', 'aquel']
  stopwords_arrays["de"] = ['p', 'aber', 'als', 'am', 'an', 'auch', 'auf', 'aus', 'bei', 'bin', 'bis', 'bist', 'da', 'dadurch', 'daher', 'darum', 'das', 'da\xc3\x9f', 'dass', 'dein', 'deine', 'dem', 'den', 'der', 'des', 'dessen', 'deshalb', 'die', 'dies', 'dieser', 'dieses', 'doch', 'dort', 'du', 'durch', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines', 'er', 'es', 'euer', 'eure', 'f\xc3\xbcr', 'hatte', 'hatten', 'hattest', 'hattet', 'hier', 'hinter', 'ich', 'ihr', 'ihre', 'im', 'in', 'ist', 'ja', 'jede', 'jedem', 'jeden', 'jeder', 'jedes', 'jener', 'jenes', 'jetzt', 'kann', 'kannst', 'k\xc3\xb6nnen', 'k\xc3\xb6nnt', 'machen', 'mein', 'meine', 'mit', 'mu\xc3\x9f', 'mu\xc3\x9ft', 'musst', 'm\xc3\xbcssen', 'm\xc3\xbc\xc3\x9ft', 'nach', 'nachdem', 'nein', 'nicht', 'nun', 'oder', 'seid', 'sein', 'seine', 'sich', 'sie', 'sind', 'soll', 'sollen', 'sollst', 'sollt', 'sonst', 'soweit', 'sowie', 'und', 'unser', 'unsere', 'unter', 'vom', 'von', 'vor', 'wann', 'warum', 'was', 'weiter', 'weitere', 'wenn', 'wer', 'werde', 'werden', 'werdet', 'weshalb', 'wie', 'wieder', 'wieso', 'wir', 'wird', 'wirst', 'wo', 'woher', 'wohin', 'zu', 'zum', 'zur', '\xc3\xbcber']
  language_arrays = {"en":{}, "fr":{}, "pt":{}, "ja":{}, "es":{}, "de":{}}
  tag_arrays = {i: {} for i in language_arrays.keys()}

  # fit the model
  start_time = time.time()
  test_messages = []
  training_messages = self.portal_catalog.searchResults(
    portal_type="Web Message",
    query=NegatedQuery(Query(subject=None)),
  )
  if not training_messages:
    return "No Web Messages found to train on"
  for index, message in enumerate(training_messages):
    if random.random() <= 0.2:
      test_messages.append(message)
    else:
      (language_arrays, tag_arrays) = message.WebMessage_trainOnWebMessage(language_arrays, tag_arrays, stopwords_arrays)

  so = {"sale", "pricing", "demo", "partnership", "advertising"}
  sr = {"help", "starting", "install", "bug"}
  m = {"job", "sponsorship", "academic", "contributor"}
  correct_tags = 0
  excess_tags = 0  
  language_accuracy = 0
  type_accuracy = 0

  for message in test_messages: 
    suggested_subject_list = []

    # clean up header from contact form, if there is one
    text = message.getTextContent()
    if text is None:
      pass
    line_array = [line for line in text.splitlines() if line.strip() != '']
    if line_array[0][:6] == "  Name":
      line_array = line_array[4:]
      line_array[0] = line_array[0][14:]
    text = ' '.join(line_array)

    # determine language of message
    message_language = "en"
    languages = language_arrays.keys()
    language_relevance = {languages[i]:0 for i in range(len(languages))}
    for word in text:
      for language in languages:
        if word in language_arrays[language]:
          word_relevance = (language_arrays[language][word])/(list(language_arrays[language].values())[0])
          language_relevance[language] = language_relevance[language] + word_relevance
    message_language = max(language_relevance, key=language_relevance.get)
    if message_language != "en":
      suggested_subject_list.append(message_language)

    # clean up text for analysis
    import string
    exclude = set(string.punctuation)
    text = text.lower()
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
    average_relevance = sum(tag_relevance.values()) / (len(tag_relevance.values()))
    for t in tag_relevance:
      if tag_relevance[t] >= average_relevance*2:
        suggested_subject_list.append(t)

    # test applied tags for accuracy
    message_tags = message.getSubjectList()
    message_tags_set = set(message_tags)
    suggested_tags_set = set(suggested_subject_list)

    correct_tags += len(suggested_tags_set.intersection(message_tags_set)) / len(message_tags_set)
    if len(suggested_tags_set) != 0:
      excess_tags += len(suggested_tags_set.difference(message_tags_set)) / len(suggested_tags_set)

    correct_language = True
    for language in languages:
      if language in message_tags_set.symmetric_difference(suggested_tags_set):
        correct_language = False
    if correct_language == True:
      language_accuracy += 1

    if message_tags_set.intersection(sr):
      if suggested_tags_set.intersection(sr):
        type_accuracy += 1
    elif message_tags_set.intersection(so):
      if suggested_tags_set.intersection(so):
        type_accuracy += 1
    else:
      if not suggested_tags_set.intersection(sr) and not suggested_tags_set.intersection(so):
        type_accuracy += 1

  if not len(test_messages) == 0:
    correct_tags = float(correct_tags) / float(len(test_messages))
    excess_tags = float(excess_tags) / float(len(test_messages))
    language_accuracy = float(language_accuracy) / float(len(test_messages))
    type_accuracy = float(type_accuracy) / float(len(test_messages))
  end_time = time.time()
  uptime = end_time - start_time
  human_uptime = str(datetime.timedelta(seconds=int(uptime)))
  
  return "Model tested in " + human_uptime + " showed a language accuracy of " + str(language_accuracy) + \
        ", and a ticket_type accuracy of " + str(type_accuracy) + ", identifying " + str(correct_tags) + " of the tags correctly with " + str(excess_tags) + " excess tags."