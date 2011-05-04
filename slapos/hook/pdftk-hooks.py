import os
def pre_make_hook(options, buildout):
  # change to pdftk directory, where built process shall be done
  os.chdir('pdftk')
