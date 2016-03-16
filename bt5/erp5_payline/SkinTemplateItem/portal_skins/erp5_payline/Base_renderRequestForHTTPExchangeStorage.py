import json
# Only storing form data now, because it's trivial and nothing is needed outside it yet.
return json.dumps({
  'form': REQUEST.form,
})
