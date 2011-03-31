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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zLOG import LOG, INFO

import os
import subprocess

def popenCommunicate(command_list, input=None, **kwargs):
  kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  popen = subprocess.Popen(command_list, **kwargs)
  result = popen.communicate(input)[0]
  if popen.returncode is None:
    popen.kill()
  if popen.returncode != 0:
    raise ValueError('Issue during calling %r, result was:\n%s' % (command_list,
      result))
  return result

class CertificateAuthorityBusy(Exception):
  """Exception raised when certificate authority is busy"""
  pass

class CertificateAuthorityDamaged(Exception):
  """Exception raised when certificate authority is damaged"""
  pass

class CertificateAuthorityTool(BaseTool):
  """CertificateAuthorityTool

  This tool assumes that in certificate_authority_path openssl configuration is ready.
  """

  id = 'portal_certificate_authority'
  meta_type = 'ERP5 Certificate Authority Tool'
  portal_type = 'Certificate Authority Tool'
  security = ClassSecurityInfo()
  allowed_types = ()
  isIndexable = 0

  certificate_authority_path = ''
  openssl_binary = ''

  manage_options = (({'label': 'Edit',
                      'action': 'manage_editCertificateAuthorityToolForm',},
                     )
                    ) + BaseTool.manage_options

  _properties = (({'id':'certificate_authority_path',
                   'type':'string',
                   'mode':'w',
                   'label':'Absolute path to certificate authority'
                   },
                   {'id':'openssl_binary',
                   'type':'string',
                   'mode':'w',
                   'label':'Absolute path to OpenSSL binary'
                   },
                  )
                 )

  def _lockCertificateAuthority(self):
    """Checks lock and locks Certificate Authority tool, raises CertificateAuthorityBusy"""
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
    """Checks Certificate Authority configuration, raises CertificateAuthorityDamaged"""
    if not self.certificate_authority_path:
      raise CertificateAuthorityDamaged('Certificate authority path is not '
        'configured')
    if not os.path.isdir(self.certificate_authority_path):
      raise CertificateAuthorityDamaged('Path to Certificate Authority %r is '
        'wrong' % self.certificate_authority_path)
    if not self.openssl_binary:
      raise CertificateAuthorityDamaged('OpenSSL binary path is not '
        'configured' % self.certificate_authority_path)
    if not os.path.isfile(self.openssl_binary):
       raise CertificateAuthorityDamaged('OpenSSL binary %r does not exists' %
        self.openssl_binary)
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

    Permissions in slap tool are simple:
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
      '../www/Vifib_editCertificateAuthorityTool',
      globals(),
      __name__='manage_editCertificateAuthorityToolForm')

  security.declareProtected(Permissions.ManageProperties, 'manage_editCertificateAuthorityTool')
  def manage_editCertificateAuthorityTool(self, certificate_authority_path, openssl_binary, RESPONSE=None):
    """Edit the object"""
    error_message = ''

    if certificate_authority_path == '' or certificate_authority_path is None:
      error_message += 'Invalid Certificate Authority'
    else:
      self.certificate_authority_path = certificate_authority_path

    if openssl_binary == '' or openssl_binary is None:
      error_message += 'Invalid OpenSSL binary'
    else:
      self.openssl_binary = openssl_binary

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

  security.declareProtected(Permissions.AccessContentsInformation, 'getNewCertificate')
  def getNewCertificate(self, common_name):
    """Returns certificate for passed common name, as dictionary of {key, certificate, id, common_name}"""
    self._checkCertificateAuthority()
    self._lockCertificateAuthority()
    try:
      new_id = open(self.serial, 'r').read().strip().lower()
      key = os.path.join(self.certificate_authority_path, 'private', new_id+'.key')
      csr = os.path.join(self.certificate_authority_path, new_id + '.csr')
      cert = os.path.join(self.certificate_authority_path, 'certs', new_id + '.crt')
      try:
        popenCommunicate([self.openssl_binary, 'req', '-nodes', '-config',
          self.openssl_config, '-new', '-keyout', key, '-out', csr, '-days',
          '3650'], '%s\n' % common_name, stdin=subprocess.PIPE)
        popenCommunicate([self.openssl_binary, 'ca', '-days', '3650',
          '-batch', '-config', self.openssl_config, '-out', cert, '-infiles',
          csr])
        os.unlink(csr)
        return dict(
          key=open(key).read(),
          certificate=open(cert).read(),
          id=new_id,
          common_name=common_name)
      except:
        try:
          for p in [key, csr, cert]:
            if os.path.exists(p):
              os.unlink(p)
        except:
          # do not raise during cleanup
          pass
        raise
    finally:
      self._unlockCertificateAuthority()

  security.declareProtected(Permissions.AccessContentsInformation, 'revokeCertificate')
  def revokeCertificate(self, serial):
    """Revokes certificate with serial, returns dictionary {crl}"""
    self._checkCertificateAuthority()
    self._lockCertificateAuthority()
    try:
      new_id = open(self.crl, 'r').read().strip().lower()
      crl_path = os.path.join(self.certificate_authority_path, 'crl')
      crl = os.path.join(crl_path, new_id + '.crl')
      cert = os.path.join(self.certificate_authority_path, 'certs', serial + '.crt')
      if not os.path.exists(cert):
        raise ValueError('Certificate with serial %r does not exists' % serial)
      try:
        popenCommunicate([self.openssl_binary, 'ca', '-config',
          self.openssl_config, '-revoke', cert])
        popenCommunicate([self.openssl_binary, 'ca', '-config',
          self.openssl_config, '-gencrl', '-out', crl])
        hash = popenCommunicate([self.openssl_binary, 'crl', '-noout',
          '-hash', '-in', crl]).strip()
        previous_id = int(len([q for q in os.listdir(crl_path) if hash in q]))
        os.symlink(crl, os.path.join(crl_path, '%s.%s' % (hash, previous_id)))
        return dict(crl=open(crl).read())
      except:
        try:
          for p in [crl]:
            if os.path.exists(p):
              os.unlink(p)
        except:
          # do not raise during cleanup
          pass
        raise
    finally:
      self._unlockCertificateAuthority()

InitializeClass(CertificateAuthorityTool)
