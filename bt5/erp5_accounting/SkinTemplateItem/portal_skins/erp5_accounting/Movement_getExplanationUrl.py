from ZTUtils import make_query

explanation = brain.getObject().getExplanationValue()
if url_dict:
  jio_key = explanation.getRelativeUrl()
  return {
    'command': 'index',
    'options': {
      'jio_key': jio_key,
    },
    'view_kw': {
      'view': 'view',
      'jio_key': jio_key,
    }
  }

if selection and selection_name:
  return "%s?%s" % (explanation.absolute_url(),
                    make_query(selection_index=selection.getIndex(),
                               selection_name=selection_name))

return explanation.getRelativeUrl()
