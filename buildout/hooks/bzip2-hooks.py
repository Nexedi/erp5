import os
import shutil
def post_make_hook(options, buildout):
  make_options_list = [q for q in options.get('make-options', '').split('\n') if q]
  if os.system('make %s -f Makefile-libbz2_so' % ' '.join(make_options_list)) != 0:
    raise ValueError('Generation of dynamic library failed')
  original = 'libbz2.so.1.0.6'
  link_list = ['libbz2.so.1.0', 'libbz2.so.1', 'libbz2.so']
  destination = os.path.join(options['location'], 'lib')
  for filename in [original] + link_list:
    f = os.path.join(destination, filename)
    if os.path.exists(f) or os.path.islink(f):
      os.unlink(f)
  shutil.copyfile(os.path.join(os.curdir, original), os.path.join(destination,
    original))

  for link in link_list:
    os.symlink(original, os.path.join(destination,
      link))
