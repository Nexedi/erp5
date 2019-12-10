# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import glob, os, subprocess, sys

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zLOG import LOG, INFO

def popenCommunicate(command_list, input=None, **kwargs):
  kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  popen = subprocess.Popen(command_list, **kwargs)
  result = popen.communicate(input)[0]
  if popen.returncode is None:
    popen.kill()
  if popen.returncode != 0:
    raise ValueError('Issue during calling %r, result was:\n%s' % (
    command_list, result))
  return result

def binary_search(binary):
  env_path_list = [p for p in os.getenv('PATH', '').split(os.pathsep)
                if os.path.isdir(p)]
  mode   = os.R_OK | os.X_OK
  for path in env_path_list:
    pathbin = os.path.join(path, binary)
    if os.access(pathbin, mode) == 1:
      return pathbin

class CertificateAuthorityBusy(Exception):
  """Exception raised when certificate authority is busy"""
  pass

class CertificateAuthorityDamaged(Exception):
  """Exception raised when certificate authority is damaged"""
  pass

class CertificateAuthorityTool(BaseTool):
  """CertificateAuthorityTool

  This tool assumes that in certificate_authority_path openssl configuration
  is ready.
  """

  id = 'portal_certificate_authority'
  meta_type = 'ERP5 Certificate Authority Tool'
  portal_type = 'Certificate Authority Tool'
  security = ClassSecurityInfo()
  allowed_types = ()
  isIndexable = 1

  certificate_authority_path = os.environ.get('CA_PATH', '')
  openssl_binary = binary_search('openssl')

  manage_options = (({'label': 'Edit',
                      'action': 'manage_editCertificateAuthorityToolForm',},
                     )
                    ) + BaseTool.manage_options

  _properties = (({'id':'certificate_authority_path',
                   'type':'string',
                   'mode':'w',
                   'label':'Absolute path to certificate authority',
                   },
                  )
                 )

  def _lockCertificateAuthority(self):
    """Checks lock and locks Certificate Authority tool

       Raises CertificateAuthorityBusy"""
    if os.path.exists(self.lock):
      raise CertificateAuthorityBusy
    open(self.lock, 'w').write('locked')

  def _unlockCertificateAuthority(self):
    """Checks lock and locks Certificate Authority tool"""
    if os.path.exists(self.lock):
      os.unlink(self.lock)
    else:
      LOG('CertificateAuthorityTool', INFO, 'Lock file %r did not existed '
        'during unlocking' % self.lock)

  def _checkCertificateAuthority(self):
    """Checks Certificate Authority configuration

       Raises CertificateAuthorityDamaged"""
    if not self.certificate_authority_path:
      raise CertificateAuthorityDamaged('Certificate authority path is not '
        'configured')
    if not os.path.isdir(self.certificate_authority_path):
      raise CertificateAuthorityDamaged('Path to Certificate Authority %r is '
        'wrong' % self.certificate_authority_path)
    self.openssl_binary = binary_search('openssl')
    self.serial = os.path.join(self.certificate_authority_path, 'serial')
    self.crl = os.path.join(self.certificate_authority_path, 'crlnumber')
    self.index = os.path.join(self.certificate_authority_path, 'index.txt')
    self.openssl_config = os.path.join(self.certificate_authority_path,
      'openssl.cnf')
    self.lock = os.path.join(self.certificate_authority_path, 'lock')
    for f in [self.serial, self.crl, self.index]:
      if not os.path.isfile(f):
        raise CertificateAuthorityDamaged('File %r does not exists.' % f)

  security.declarePrivate('manage_afterAdd')
  def manage_afterAdd(self, item, container) :
    """Init permissions right after creation.

    Permissions in tool are simple:
     o Each member can access the tool.
     o Only manager can view and create.
     o Anonymous can not access
    """
    item.manage_permission(Permissions.AddPortalContent,
          ['Manager'])
    item.manage_permission(Permissions.AccessContentsInformation,
          ['Member', 'Manager'])
    item.manage_permission(Permissions.View,
          ['Manager',])
    BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)

  #'Edit' option form
  manage_editCertificateAuthorityToolForm = PageTemplateFile(
      '../www/CertificateAuthorityTool_editPropertyList',
      globals(),
      __name__='manage_editCertificateAuthorityToolForm')

  security.declareProtected(Permissions.ManageProperties,
      'manage_editCertificateAuthorityTool')
  def manage_editCertificateAuthorityTool(self, certificate_authority_path,
      RESPONSE=None):
    """Edit the object"""
    error_message = ''

    if certificate_authority_path == '' or certificate_authority_path is None:
      error_message += 'Invalid Certificate Authority'
    else:
      self.certificate_authority_path = certificate_authority_path

    #Redirect
    if RESPONSE is not None:
      if error_message != '':
        self.REQUEST.form['manage_tabs_message'] = error_message
        return self.manage_editCertificateAuthorityToolForm(RESPONSE)
      else:
        message = "Updated"
        RESPONSE.redirect('%s/manage_editCertificateAuthorityToolForm'
                          '?manage_tabs_message=%s'
                          % (self.absolute_url(), message)
                          )

  security.declareProtected(Permissions.AccessContentsInformation,
      'getNewCertificate')
  def getNewCertificate(self, common_name):
    # No docstring in order to make this method non publishable
    # Returns certificate for passed common name, as dictionary of
    #      {key, certificate, id, common_name}
    if not common_name:
      raise ValueError("Invalid common name: %r" % common_name)
    self._checkCertificateAuthority()
    self._lockCertificateAuthority()

    index = open(self.index).read().splitlines()
    valid_line_list = [q for q in index if q.startswith('V') and
      ('CN=%s/' % common_name in q)]
    if len(valid_line_list) >= 1:
      self._unlockCertificateAuthority()
      raise ValueError('The common name %r already has a certificate'
                       'please revoke it before request a new one..' % common_name)

    try:
      new_id = open(self.serial, 'r').read().strip().lower()
      key = os.path.join(self.certificate_authority_path, 'private',
          new_id+'.key')
      csr = os.path.join(self.certificate_authority_path, new_id + '.csr')
      cert = os.path.join(self.certificate_authority_path, 'certs',
          new_id + '.crt')
      try:
        os.close(os.open(key, os.O_CREAT | os.O_EXCL, 0600))
        popenCommunicate([self.openssl_binary, 'req', '-utf8', '-nodes', '-config',
          self.openssl_config, '-new', '-keyout', key, '-out', csr, '-days',
          '3650'], '%s\n' % common_name, stdin=subprocess.PIPE)
        popenCommunicate([self.openssl_binary, 'ca', '-utf8', '-days', '3650',
          '-batch', '-config', self.openssl_config, '-out', cert, '-infiles',
          csr])
        os.unlink(csr)
        return dict(
          key=open(key).read(),
          certificate=open(cert).read(),
          id=new_id,
          common_name=common_name)
      except:
        e = sys.exc_info()
        try:
          for p in key, csr, cert:
            if os.path.exists(p):
              os.unlink(p)
        except:
          # do not raise during cleanup
          pass
        raise e[0], e[1], e[2]
    finally:
      self._unlockCertificateAuthority()

  security.declareProtected(Permissions.AccessContentsInformation,
      'revokeCertificate')
  def revokeCertificate(self, serial):
    # No docstring in order to make this method non publishable
    # Revokes certificate with serial, returns dictionary {crl}
    self._checkCertificateAuthority()
    self._lockCertificateAuthority()
    try:
      new_id = open(self.crl, 'r').read().strip().lower()
      crl_path = os.path.join(self.certificate_authority_path, 'crl')
      crl = os.path.join(crl_path, new_id + '.crl')
      cert = os.path.join(self.certificate_authority_path, 'certs',
          serial.lower() + '.crt')
      if not os.path.exists(cert):
        raise ValueError('Certificate with serial %r does not exist' % serial)
      created = [crl]
      popenCommunicate([self.openssl_binary, 'ca', '-config',
        self.openssl_config, '-revoke', cert])
      try:
        popenCommunicate([self.openssl_binary, 'ca', '-utf8', '-config',
          self.openssl_config, '-gencrl', '-out', crl])
        alias = os.path.join(crl_path, popenCommunicate([self.openssl_binary,
          'crl', '-noout', '-hash', '-in', crl]).strip() + '.')
        alias += str(len(glob.glob(alias + '*')))
        created.append(alias)
        os.symlink(os.path.basename(crl), alias)
        return dict(crl=open(crl).read())
      except:
        e = sys.exc_info()
        try:
          for p in 'index.txt', 'crlnumber':
            p = os.path.join(self.certificate_authority_path, p)
            os.rename(p + '.old', p)
          for p in created:
            if os.path.exists(p):
              os.unlink(p)
        except:
          # do not raise during cleanup
          pass
        raise e[0], e[1], e[2]
    finally:
      self._unlockCertificateAuthority()

  def _getValidSerial(self, common_name):
    index = open(self.index).read().splitlines()
    valid_line_list = [q for q in index if q.startswith('V') and
      ('CN=%s/' % common_name in q)]
    if len(valid_line_list) != 1:
      raise ValueError('No certificate for %r' % common_name)
    return valid_line_list[0].split('\t')[3]

  security.declareProtected(Permissions.AccessContentsInformation,
    'revokeCertificate')
  def revokeCertificateByCommonName(self, common_name):
    self._checkCertificateAuthority()
    serial = self._getValidSerial(common_name)
    self.revokeCertificate(serial)

  # XXX: This class lacks a corresponding portal type, so its instances are not
  # actual documents. A portal type should be created from it, and backward
  # compatibility added to keep existing instances working.
  # Until then, hardcode some methods expected to exist on all document
  # classes so that they can be removed from Base.
  def _getAcquireLocalRoles(self):
    return True

InitializeClass(CertificateAuthorityTool)
