import os
def pre_configure_hook(options, buildout):
  # remove certificate generation
  # based on Gentoo: http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/net-misc/stunnel/stunnel-4.33.ebuild
  name = os.path.join('tools','Makefile.in')
  f = file(name, 'r')
  d = f.read().replace('install-data-local:', 'do-not-run-this:')
  f.close()
  file(name, 'w').write(d)
