import os
def pre_make_hook(options, buildout):
  # workaround python's tarfile bug with links
  os.symlink('../LICENSE', os.path.join('conf', 'LICENSE'))
  os.symlink('../TLS_LICENSE', os.path.join('conf', 'TLS_LICENSE'))
