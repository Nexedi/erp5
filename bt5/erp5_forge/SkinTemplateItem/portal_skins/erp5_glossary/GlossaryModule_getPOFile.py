from DateTime import DateTime
MESSAGE_TEMPLATE = '''\
msgid %(english)s
msgstr %(translation)s
'''

def formatMessage(english, translation, term=None):
  if term is not None:
    return '''\
#: %s [Glossary term %s]
msgid %s
msgstr %s
''' % (term.getComment(), term.getId(), english, translation)
  return MESSAGE_TEMPLATE % dict(english=english, translation=translation)


def formatString(string):
  line_list = string.splitlines(True)
  length = len(line_list)
  if length==1:
    return '"%s"' % string.replace('"', '\\"').replace('\n', '\\n')
  else:
    return '\n'.join(['""']+[formatString(i) for i in line_list])

# po header
now = DateTime().toZone('UTC').strftime("%Y-%m-%d %H:%M+0000")
print(MESSAGE_TEMPLATE % (dict(english='""',
                               translation=
r'''"Project-Id-Version: ERP5 Localized Interface\n"
"POT-Creation-Date: %s\n"
"PO-Revision-Date: %s\n"
"Last-Translator:  <>\n"
"Language-Team: %s <>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
''' % (now, now, language))))
catalog = context.portal_catalog

for i in catalog(portal_type='Glossary Term',
                 validation_state='validated',
                 business_field_id=business_field_list,
                 language_id=language):
  term = i.getObject()
  reference = term.getReference()

  english_term = catalog.getResultValue(portal_type='Glossary Term',
                                        validation_state='validated',
                                        language_id='en',
                                        reference=reference,
                                        business_field_uid=term.getBusinessFieldUid())
  if english_term is None:
    continue

  translated_title = term.getTitle()
  translated_description = term.getDescription()

  english_title = english_term.getTitle()
  english_description = english_term.getDescription()
  english_relative_url = english_term.getRelativeUrl()

  if translated_title:
    if not english_title:
      raise ValueError('Title of corresponding English term(%s) to "%s" is empty.' % (english_relative_url, translated_title))
    if translated_title!=english_title:
      print(formatMessage(english=formatString(english_title),
                          translation=formatString(translated_title),
                          term=term))

  if translated_description:
    if not english_description:
      raise ValueError('Description of corresponding English term(%s) to "%s" is empty.' % (english_relative_url, translated_description))

    if translated_description!=english_description:
      print(formatMessage(english=formatString(english_description),
                          translation=formatString(translated_description),
                          term=term))

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-disposition', 'attachment;filename=translation.po')
RESPONSE.setHeader('Content-Type', 'text/x-gettext-translation;charset=utf-8')

return printed
