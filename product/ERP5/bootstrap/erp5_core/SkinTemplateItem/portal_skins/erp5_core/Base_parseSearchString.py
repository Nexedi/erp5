"""
  Make SQLCatalog parse given search string and generate an Abstract Syntax Tree.
  Then, walk this tree and categorize criterion by type (and their alias, see code).

  Example:
  * input:
  word_to_search_for "exact_phrase" +containing_all_the_words -without_word created:1w reference:nxd-test version:001 language:en contributor_title:John mine:yes newest:yes

  * output
   {'newest': 'yes',
   'reference': 'nxd-test',
   'language': 'en',
   'mine': 'yes',
   'searchabletext': 'word_to_search_for exact_phrase +containing_all_the_words -without_word John',
   'version': '001',
   'creation_from': DateTime('2010/02/23 13:11:11.698 GMT+2')}
"""
from DateTime import DateTime

def render_filetype_list(filetype_list):
  return ['%%.%s' % (x, ) for x in filetype_list]

def render_state_list(state_list):
  # Note: also used to render type list
  result = []
  append = result.append
  for state in state_list:
    if state != 'all':
      append(state)
  return result

def render_date_range(date_range_list):
  result = []
  append = result.append
  now = DateTime()
  for date_range in date_range_list:
    # XXX: original version used a regex, but we can't import
    # "re" module here, so fallback on hand-crafted parsing.
    # Original regex: '(\d)([wmy]).*'
    # State meaning:
    #   0: we expect only decimals
    #   1: we expect one of 'w', 'm', or 'y'
    state = 0
    duration_char_list = []
    multiplicator = None
    for char in date_range:
      if state == 0:
        if '0' <= char <= '9':
          duration_char_list.append(char)
        else:
          state = 1
      if state == 1:
        if len(duration_char_list):
          if char == 'w':
            multiplicator = 7
          elif char == 'm':
            multiplicator = 30
          elif char == 'y':
            multiplicator = 365
        break
    if multiplicator is not None:
      duration = int(''.join(duration_char_list))
      append(now - duration * multiplicator)
  return result

criterion_alias_dict = {
  'state':            ('simulation_state', render_state_list),
  'type':             ('portal_type',      render_state_list),
  'filetype':         ('source_reference', render_filetype_list),
  'file':             ('source_reference', None),
  'created':          ('creation_from',    render_date_range),
  'simulation_state': (True, None),
  'language':         (True, None),
  'version':          (True, None),
  'reference':        (True, None),
  'portal_type':      (True, None),
  'source_reference': (True, None),
  'creation_from':    (True, None),
  'searchabletext':   (True, None),
  # indicates user search only within owned documents
  'mine':             (True, None),
  # indicates user search only the newest versions
  'newest':           (True, None),
  # indicates user search for documents by contributor title
  'contributor_title':(True, None),
  # indicates user search mode (boolean or with with query expansion)
  'mode':             (True, None),
}

DEFAULT_CRITERION_ALIAS = 'searchabletext'

def resolveCriterion(criterion_alias, criterion_value_list):
  initial_criterion_alias = criterion_alias
  # XXX: should be a set
  seen_alias_dict = {} # Protection against endless loops
  while True:
    next_alias, value_list_renderer = criterion_alias_dict.get(criterion_alias, (DEFAULT_CRITERION_ALIAS, None))
    if value_list_renderer is not None:
      criterion_value_list = value_list_renderer(criterion_value_list)
    if next_alias is True:
      break
    seen_alias_dict[criterion_alias] = None
    if next_alias in seen_alias_dict:
      raise RuntimeError('Endless alias loop detected: lookup of %r reached alias %r twice' % (initial_criterion_alias, next_alias))
    criterion_alias = next_alias
  return criterion_alias, criterion_value_list

def recurseSyntaxNode(node, criterion=DEFAULT_CRITERION_ALIAS):
  if node.isColumn():
    result = recurseSyntaxNode(node.getSubNode(), criterion=node.getColumnName())
  else:
    result = {}
    if node.isLeaf():
      result[criterion] = [node.getValue()]
    else:
      for subnode in node.getNodeList():
        for criterion, value_list in recurseSyntaxNode(subnode, criterion=criterion).items():
          result.setdefault(criterion, []).extend(value_list)
  return result

def acceptAllColumns(column):
  return True

node = context.getPortalObject().portal_catalog.getSQLCatalog().parseSearchText(searchstring, search_key='FullTextKey', is_valid=acceptAllColumns)
result =  {}
if node is None:
  result['searchabletext'] = searchstring
else:
  for criterion, value_list in recurseSyntaxNode(node).items():
    criterion, value_list = resolveCriterion(criterion, value_list)
    result.setdefault(criterion, []).extend(value_list)
  filtered_result = {}
  for criterion, value_list in result.items():
    if len(value_list) > 0:
      filtered_result[criterion] = value_list
  result = filtered_result
  for criterion, value_list in result.items():
    # XXX: yuck
    if criterion == 'searchabletext':
      result['searchabletext'] = ' '.join(value_list)
    if len(value_list) == 1:
      result[criterion] = value_list[0]
  if 'searchabletext' not in result:
    result['searchabletext'] = ''
return result
