"""
  Due to limitation of edos test runner in buildbot we manually 
  call this method that will set SVN revision number used for this 'Test Result' object. 
"""
if revision and not context.getIntIndex():
  context.setIntIndex(revision)

context.edit(buildslave_name = buildslave_name)
