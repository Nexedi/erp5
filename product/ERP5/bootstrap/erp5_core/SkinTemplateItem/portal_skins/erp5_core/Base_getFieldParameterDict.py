"""
  Get default relation string field parameters
  based on its id
"""
pieces = context.getId().split('_')
prefix = pieces.pop(0)
if prefix != 'my' and prefix != 'listbox':
  return {} # this should not happen

if pieces[-1] == 'list':
  pieces.pop()

# can it be translated title, or something else?
if pieces[-1] in ('title', 'reference'):
  idx = -1
else:
  idx = -2
  pieces += 'relative', 'url'

return {'base_category': '_'.join(pieces[:idx]),
        'catalog_index': '_'.join(pieces[idx:])}
