person = sci['object']
if sci['object'].getReference():
  person.activate(after_path_and_method_id=(person.getPath(),
                                   ('immediateReindexObject',
                                    'recursiveImmediateReindexObject'))).Person_createUserPreference()
