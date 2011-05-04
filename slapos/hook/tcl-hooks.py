import os
import shutil
def pre_configure_hook(options, buildout):
  os.chdir('unix')

def post_make_hook(options, buildout):
  bindir = os.path.join(options['location'], 'bin')
  destination = os.path.join(bindir, 'tclsh')
  if not os.path.exists(destination):
    original = os.path.join(bindir, [q for q in os.listdir(bindir) if q.startswith('tclsh')][0])
    shutil.copy(original, destination)
