from ZTUtils import make_query
if selection and selection_name:
  return "%s?%s" % (brain.getObject().getExplanationValue().absolute_url(),
                    make_query(selection_index=selection.getIndex(),
                               selection_name=selection_name))

return brain.getObject().getExplanation()
