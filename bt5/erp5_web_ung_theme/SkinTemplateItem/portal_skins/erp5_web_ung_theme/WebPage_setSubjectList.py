"""
  Wrapper to store the subject list in context, because isn't possible 
  pass list in POST correctly.
"""
context.setSubjectList(value.split(","))
