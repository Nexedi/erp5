if context.InternetMessagePost_ingest():
  getattr(context, 'import')() # "context.import()" is considered a syntax error...
else:
  context.failImport()
