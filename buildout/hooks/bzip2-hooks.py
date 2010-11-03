import os
import shutil
def post_make_hook(options, buildout):
  make_options_list = [q for q in options.get('make-options', '').split('\n') if q]
  if os.system('make %s -f Makefile-libbz2_so' % ' '.join(make_options_list)) != 0:
    raise ValueError('Generation of dynamic library failed')
  for f in [q for q in os.listdir(os.curdir) if '.so' in q]:
    shutil.copyfile(f, os.path.join(options['location'], 'lib', f))
