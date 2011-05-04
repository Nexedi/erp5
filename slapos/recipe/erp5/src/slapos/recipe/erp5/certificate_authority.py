import os
import subprocess
import time


def popenCommunicate(command_list, input=None):
  subprocess_kw = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  if input is not None:
    subprocess_kw.update(stdin=subprocess.PIPE)
  popen = subprocess.Popen(command_list, **subprocess_kw)
  result = popen.communicate(input)[0]
  if popen.returncode is None:
    popen.kill()
  if popen.returncode != 0:
    raise ValueError('Issue during calling %r, result was:\n%s' % (command_list,
      result))
  return result


def checkCertificateAuthority(ca_conf):
  file_list = [
      ca_conf['ca_key'],
      ca_conf['ca_certificate'],
  ]
  ca_ready = True
  for f in file_list:
    if not os.path.exists(f):
      ca_ready = False
      break
  if ca_ready:
    return
  for f in file_list:
    if os.path.exists(f):
      os.unlink(f)
  try:
    # no CA, let us create new one
    popenCommunicate([ca_conf['openssl_binary'], 'req', '-nodes', '-config',
        ca_conf['openssl_configuration'], '-new', '-x509', '-extensions',
        'v3_ca', '-keyout', ca_conf['ca_key'], '-out',
        ca_conf['ca_certificate'], '-days',
        '10950'], 'Automatic Certificate Authority\n')
  except:
    try:
      for f in file_list:
        if os.path.exists(f):
          os.unlink(f)
    except:
      # do not raise during cleanup
      pass
    raise


def checkCertificate(common_name, key, certificate, ca_conf):
  file_list = [key, certificate]
  ready = True
  for f in file_list:
    if not os.path.exists(f):
      ready = False
      break
  if ready:
    return
  for f in file_list:
    if os.path.exists(f):
      os.unlink(f)
  csr = certificate + '.csr'
  try:
    popenCommunicate([ca_conf['openssl_binary'], 'req', '-config',
      ca_conf['openssl_configuration'], '-nodes', '-new', '-keyout',
      key, '-out', csr, '-days', '3650'],
      common_name + '\n')
    try:
      popenCommunicate([ca_conf['openssl_binary'], 'ca', '-batch', '-config',
        ca_conf['openssl_configuration'], '-out', certificate,
        '-infiles', csr])
    finally:
      if os.path.exists(csr):
        os.unlink(csr)
  except:
    try:
      for f in file_list:
        if os.path.exists(f):
          os.unlink(f)
    except:
      # do not raise during cleanup
      pass
    raise


def checkLoginCertificate(ca_conf):
  checkCertificate('Login Based Access', ca_conf['login_key'],
      ca_conf['login_certificate'], ca_conf)


def checkKeyAuthCertificate(ca_conf):
  checkCertificate('Key Based Access', ca_conf['key_auth_key'],
      ca_conf['key_auth_certificate'], ca_conf)


def runCertificateAuthority(args):
  ca_conf = args[0]
  while True:
    checkCertificateAuthority(ca_conf)
    checkLoginCertificate(ca_conf)
    checkKeyAuthCertificate(ca_conf)
    time.sleep(60)
