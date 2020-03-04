# This script checks for naming validity.
#
# NOTE: Do not rely on this script too much! After all, human must take care.

# TODO:
# - Add more abbriviation words.
# - Check language dependencies (e.g. "Account Of" should not be allowed, because it cannot be
#   translated naturally for other languages).
# - Check skin names.
# - Check script names (from skin folders and workflows).
import re
ABBREVIATION_WORD_SET = ((
  "BBAN", "BIC", "BOM", "CAD", "CRM", "CSS", "CSV", "CTX", "DMS", "DNS",
  "EAN", "ERP5", "FAX", "GAP", "GID", "GPG", "HTML", "HTTP", "IBAN", "ID",
  "IMAP", "IP", "KM", "MIME", "MRP", "NVP", "ODT", "PDF", "PDM", "PO",
  "RAM", "RSS", "SMS", "SOAP", "SQL", "SVN", "TALES", "TCP", "TSV", "UBM",
  "UID", "UOM", "URI", "URL", "VADS", "VAT", "VCS", "VPN", "XML", "ZODB",
))

# List of words that do not need to be titlecased
LOWERCASE_WORD_SET = set(('g', 'cm', 'kg', '%', '/', '...', 'm', '-', 'g/m2', 'iCalendar', 'm&#179;', 'kB'))

# List of words that should not be modified
SPECIALCASE_WORD_SET = set(("ChangeLog", "EGov", "iCal", "included",
  "JavaScript", "LibreOffice", "OAuth", "OpenAM", "OpenOffice", "SyncML",
  "TioSafe", "will"))

CLOSED_CLASS_WORD_LIST = """
  a about above across after against all along alongside already although
  amid among amongst an and another any anybody anyone anything are around as
  at be because been before behind below beneath beside between beyond both but
  by concerning could despite did do does down during each either enough every
  everybody everyone everything except few fewer following for former from
  goodbye half has have he her hers herself him himself his if in including
  inside instead into is it its itself latter less like little lots many me
  mine minus more most much my myself near neither no nobody none nor not
  nothing now of off on once one only onto opposite or our ours ourselves out
  outside over own past per plenty plus rather regarding round same several she
  should since so some somebody someone something soon such than that the their
  theirs them themselves there these they this those though through throughout
  to too toward towards under underneath unless unlike until up upon us via we
  well what whatever when where whereas whether which while whilst who whoever
  whom whose with within without worth would yes you your yours yourself
  """.split()
CLOSED_CLASS_WORD_SET = set(CLOSED_CLASS_WORD_LIST)
assert len(CLOSED_CLASS_WORD_SET) == len(CLOSED_CLASS_WORD_LIST)
SENTENCE_PART_LIST = (
  "doesn't",

  "according to", "ahead of", "apart from", "as long as", "as opposed to",
  "away from", "be triggered on", "by means of", "by way of", "contrary to", "depending on",
  "due to", "each other", "even if", "even though", "even when", "given that",
  "in accordance with", "in addition to", "in case", "in charge of",
  "in conjunction with", "in connection with", "in favour of", "in front of",
  "in line with", "in relation to", "in respect of", "in response to",
  "in search of", "in spite of", "in support of", "in terms of",
  "in the light of", "in touch with", "in view of", "let alone", "next to",
  "on behalf of", "on the part of", "on top of", "other than", "prior to",
  "provided that", "relative to", "so long as", "subject to", "with regard to",
  "with respect to",
)
SENTENCE_PART_SET = set(SENTENCE_PART_LIST)
assert len(SENTENCE_PART_SET) == len(SENTENCE_PART_LIST)

# List of allowed characters, usefull to detect non-english strings
ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789%/. ()-_?&'#,;")

def checkField(folder, form, field):
  """
    Generic function that test the validity of ERP5Form fields.
  """
  path = folder.id + '/' + form.id
  error_message = checkTitle(path, field.id, field.title(), field)
  template_field = getFieldFromProxyField(field)
  if path.endswith("FieldLibrary"):
    if not(template_field is field):
      if not(1 in [field.id.startswith(x) for x in ('my_view_mode_',
                           'my_core_mode_', 'my_report_mode_', 'my_list_mode_', 'my_dialog_mode_')]):
        error_message += "%s: %s : Bad ID for a Field Library Field" % (path, field.id)
  if template_field is None:
    if field.get_value('enabled'):
      error_message += "Could not get a field from a proxy field %s" % field.id
  else:
    if isListBox(field):
      a = template_field.getListMethodName()
      path += '/listbox'
      for x in 'columns', 'all_columns':
        for id_, title in field.get_value(x):
          error_message += checkTitle(path, x, title, field, form)
      if a not in (None, "portal_catalog", "searchFolder", "objectValues",
                   "contentValues", "ListBox_initializeFastInput"):
        if not a.endswith('List'):
          if 0:
            error_message += "%s : %s : %r Bad Naming Convention\n" % (path, id_, a)
  return error_message

def isListBox(field):
  template_field = getFieldFromProxyField(field)
  return template_field is not None and template_field.meta_type == 'ListBox'

def getFieldFromProxyField(field):
  if field.meta_type == 'ProxyField':
    field = field.getRecursiveTemplateField()
  return field

titlecase_sub = re.compile(r"[A-Za-z]+('[A-Za-z]+)?").sub
titlecase_repl = lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower()
titlecase = lambda s: titlecase_sub(titlecase_repl, s)

def checkTitle(path, id_, title, field=None, form=None):
  """
    Generic function that test the validity of a title.
  """
  error_message = ''
  if (form is not None and form.pt not in ('form_dialog', 'folder_workflow_action_dialog')) or form is None:
    if (field is not None and not field.get_value('hidden') and \
     (title is None or len(title.strip()) == 0)) or (field is None and (title is None or len(title.strip()) == 0)):
      return "%s : %s : can't be empty\n" % (path, id_)

  for c in title:
    if c.lower() not in ALLOWED_CHARS:
      return "%s : %s : %r character not allowed\n" % (path, id_, c)

  title = re.sub(re.compile(r"\b(" + "|".join(re.escape(x) for x in SENTENCE_PART_SET) + r")\b"), "", title)

  word_list = title.split(' ')
  for word in word_list:
    word = word.strip('()')

    if word.isdigit():
      continue

    if word.upper() in ABBREVIATION_WORD_SET:
      if not word.isupper():
        error_message += '%s : %s : %r is not upper case even though it is an abbriviation\n' % (path, id_, word)
    elif word.endswith('s') and word[:-1].upper() in ABBREVIATION_WORD_SET:
      if not word[:-1].isupper():
        error_message += '%s : %s : %r is not upper case even though it is an abbriviation\n' % (path, id_, word)
    elif "-" in word and word.split("-")[0].upper() in ABBREVIATION_WORD_SET:
      if not word.split("-")[0].isupper():
        error_message += '%s : %s : %r is not upper case even though it is an abbriviation\n' % (path, id_, word)
    else:
      if word.lower() in CLOSED_CLASS_WORD_SET and word != word_list[0] :
        if (word.capitalize()== word or titlecase(word)== word):
          error_message += '%s : %s : %r is a closed-class word and should not be titlecased\n' % (path, id_, word)
      elif (word.capitalize()!= word and titlecase(word)!= word) and \
         word not in LOWERCASE_WORD_SET and word not in SPECIALCASE_WORD_SET and word not in CLOSED_CLASS_WORD_SET :
        error_message += '%s : %s : %r is not titlecased\n' % (path, id_, word)
  if len(word_list) > 1 and word_list[-1].upper() == 'LIST' and word_list[-2].upper() != 'PACKING':
    error_message += '%s : %s : %r is a jargon\n' % (path, id_, title)
  return error_message



message_list = []


# Test portal_skins content
for folder in context.portal_skins.objectValues(spec=('Folder',)):
  if not folder.id.startswith('erp5_'):
    continue
  for form in folder.objectValues(spec=('ERP5 Form',)):
    if form.pt in ('embedded_form_render', 'ical_view', 'rss_view'):
      continue
    message = checkTitle('/'.join([folder.id, form.id]), 'Title of the Form itself', form.title)
    if message:
      message_list.append(message)
    if form.id.endswith("FieldLibrary"):
      if not(form.id.startswith("Base_")):
        message_list.append("%s/%s : Bad Form ID for a Field Library Form" % (folder.id, form.id))
    for group in form.get_groups():
      if group == 'hidden':
        continue
      for field in form.get_fields_in_group(group, include_disabled=True):
        if field.get_value('hidden') or field.id == 'matrixbox':
          continue
        message = checkField(folder, form, field)
        if message:
          message_list.append(message)


# Test worflow related stuff
for wf in context.portal_workflow.objectValues():

  # Test workflow states
  wf_states = wf.states
  message = ''
  if wf_states not in (None, (), [], ''):
    for state in wf_states.objectValues() :
      message += checkTitle('/'.join(['portal_workflow', wf.id, 'states', state.id]), 'title', state.title)
    if message:
      message_list.append(message)

#   # Test workflow states
#   wf_scripts = wf.scripts
#   message = ''
#   if wf_scripts not in (None, (), [], ''):
#     for script in wf_scripts.objectValues():
#       message += checkTitle('/'.join(['portal_workflow', wf.id, 'scripts', script.id]), 'id', script.id)
#     if message:
#       message_list.append(message)


# Test portal types
IGNORE_PORTAL_TYPE_SET = set(("Application Id Generator",
  "Conceptual Id Generator", "DateTime Divergence Tester",
  "Distributed Ram Cache", "Fax", "Fax Message", "Id Tool", "OAuth Tool",
  "OOo Document", "Ram Cache", "SQL Non Continuous Increasing Id Generator",
  "Url Registry Tool", "ZODB Continuous Increasing Id Generator"))
for ptype in context.portal_types.objectValues():
  pt_id = ptype.id
  if pt_id in IGNORE_PORTAL_TYPE_SET:
    continue
  pt_title = ptype.title
  message = ''
  if pt_title not in (None, ''):
    message += checkTitle('/'.join(['portal_types', pt_id]), 'title', pt_title)
  #else:
  #  message += checkTitle('/'.join(['portal_types', pt_id]), 'id', pt_id)
  if message:
    message_list.append(message)

if batch_mode:
  return message_list
if message_list:
  return ("%d problems found:\n\n" % len(message_list)) + '\n'.join(message_list)
return "OK"
