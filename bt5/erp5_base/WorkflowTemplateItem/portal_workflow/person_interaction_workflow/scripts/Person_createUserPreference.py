person = sci['object']
if person.Person_getUserId():
  person.activate(after_path_and_method_id=(person.getPath(),
                                   ('immediateReindexObject',
                                    'recursiveImmediateReindexObject'))).Person_createUserPreference()
