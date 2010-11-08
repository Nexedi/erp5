import os
def pre_configure_hook(oprtions, buildout):
  # fixes python bug related to not creating symlink contained in tarfiles
  for missing in 'configure.ac', 'Makefile.in':
    if not os.path.exists(os.path.join(os.path.curdir, missing)):
      os.symlink(os.path.join(os.path.curdir, 'base', missing),
          os.path.join(os.path.curdir, missing))
