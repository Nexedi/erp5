"""
  This scruipt is used by widgets which require access to
  the project module. Anonymous users are usually not
  allowed to list projects. To prevent raising
  exceptions, we use this script as a precondition.
"""
return context.getPortalObject().restrictedTraverse('project_module', None) is not None
