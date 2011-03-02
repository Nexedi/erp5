import os
def execute(args):
  """Portable execution with process replacement"""
  # Note: Candidate for slapos.lib.recipe
  os.execv(args[0], args)
