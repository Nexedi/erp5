import os
import shutil
def post_make_hook(options, buildout):
  destination = options['location']
  directory_list = ['include', 'lib']
  for d in directory_list:
    dd = os.path.join(destination, d)
    if not os.path.isdir(dd):
      os.mkdir(dd)
  for include in ['jbig.h', 'jbig85.h', 'jbig_ar.h']:
    shutil.copyfile(os.path.join(os.curdir, 'libjbig', include),
        os.path.join(destination, 'include', include))
  for so in ['libjbig85.so', 'libjbig.so']:
    shutil.copyfile(os.path.join(os.curdir, 'libjbig', so),
        os.path.join(destination, 'lib', so))
