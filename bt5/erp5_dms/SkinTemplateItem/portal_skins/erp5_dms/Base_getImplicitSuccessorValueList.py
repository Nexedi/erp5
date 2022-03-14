"""
  Called by document.getImplicitSuccessorValueList
  Gets a list of dicts containing reference and/or version and/or language
  and maybe some more things.
  Returns a list of objects.

  dummy simple implementation - if no version, then return the newest in the chosen language
  or in any language if not specified
"""
my_reference = context.getReference()
temporary_dict = {}
for dic in reference_list:
  reference = dic.get('reference')
  if reference is not None and reference!=my_reference:
    temporary_dict[reference] = None

if not temporary_dict:
  return ()

# For the present, we only use reference.
# Result document will be the latest version with appropriate language by user setting.)
return context.Base_zGetImplicitSuccessorValueList(reference_list=list(temporary_dict.keys()))
