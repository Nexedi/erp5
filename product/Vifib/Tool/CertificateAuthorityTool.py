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
from zLOG import LOG, INFO, ERROR

import os
import subprocess
import base64

class CertificateGenerationError(Exception):
  """Exception raised when certificate authority failed to work"""
  pass

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

  certificate_authority_path = ''
  
  manage_options = (({'label': 'Edit',
                      'action': 'manage_editCertificateAuthorityToolForm',},
                     )
                    ) + BaseTool.manage_options

  _properties = (({'id':'certificate_authority_path',
                   'type':'string',
                   'mode':'w',
                   'label':'Path to certificate authority'
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
        'configured' % self.certificate_authority_path)
    if not os.path.isdir(self.certificate_authority_path):
      raise CertificateAuthorityDamaged('Path to Certificate Authority %r is '
        'wrong' % self.certificate_authority_path)
    self.serial = os.path.join(self.certificate_authority_path, 'serial')
    self.crl = os.path.join(self.certificate_authority_path, 'crlnumber')
    self.index = os.path.join(self.certificate_authority_path, 'index.txt')
    self.openssl = os.path.join(self.certificate_authority_path, 'openssl')
    self.openssl_config = os.path.join(self.certificate_authority_path,
      'openssl.cnf')
    self.lock = os.path.join(self.certificate_authority_path, 'lock')
    for f in [self.serial, self.crl, self.index]:
      if not os.path.isfile(f):
        raise CertificateAuthorityDamaged('File %r does not exists.' % f)
    if not os.path.isfile(self.openssl):
      raise CertificateAuthorityDamaged('Openssl wrapper %r does not exists' %
        self.openssl)

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
  def manage_editCertificateAuthorityTool(self, certificate_authority_path, RESPONSE=None):
    """Edit the object"""
    error_message = ''

    #Save certificate_authority_path
    if certificate_authority_path == '' or certificate_authority_path is None:
      error_message += 'Invalid path '
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

  security.declareProtected(Permissions.AccessContentsInformation, 'getNewCertificate')
  def getNewCertificate(self):
    """Returns dictionary {key, certificate, id} where id is certificate id to be used"""
    self._checkCertificateAuthority()
    self._lockCertificateAuthority()
    try:
      new_id = open(self.serial, 'r').read().strip()
      cn = base64.encodestring(str(new_id) + ':')
      key = os.path.join(self.certificate_authority_path, 'private', new_id+'.key')
      csr = os.path.join(self.certificate_authority_path, new_id + '.csr')
      cert = os.path.join(self.certificate_authority_path, 'certs', new_id + '.crt')
      try:
        keygen = subprocess.Popen([self.openssl, 'req', '-nodes', '-config',
          self.openssl_config, '-new', '-keyout', key, '-out', csr, '-days',
          '3650'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
          stdin=subprocess.PIPE)
        result = keygen.communicate('%s\n' % cn)[0]
        if keygen.returncode is None or keygen.returncode != 0:
          LOG('CertificateAuthorityTool', ERROR, 'Issue during key generation, result was:%r' % result)
          keygen.kill()
          raise CertificateGenerationError
        keysign = subprocess.Popen([self.openssl, 'ca', '-batch', '-config',
          self.openssl_config, '-out', cert, '-infiles', csr], stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT)
        result = keysign.communicate()[0]
        if keysign.returncode is None or keysign.returncode != 0:
          LOG('CertificateAuthorityTool', ERROR, 'Issue during key signing, result was:%r' % result)
          keygen.kill()
          raise CertificateGenerationError
        os.unlink(csr)
        return dict(
          key=open(key).read(),
          certificate=open(cert).read(),
          id=new_id)
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
      new_id = open(self.crl, 'r').read().strip()
      crl = os.path.join(self.certificate_authority_path, 'crl', new_id + '.crl')
      cert = os.path.join(self.certificate_authority_path, 'certs', serial + '.crt')
      if not os.path.exists(cert):
        raise ValueError('Certificate with serial %r does not exists' % serial)
      try:
        crl_update = subprocess.Popen([self.openssl, 'ca', '-config',
          self.openssl_config, '-revoke', cert], stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT)
        result = crl_update.communicate()[0]
        if crl_update.returncode is None or crl_update.returncode != 0:
          LOG('CertificateAuthorityTool', ERROR, 'Issue during CRL update, result was:%r' % result)
          crl_update.kill()
          raise CertificateGenerationError
        crl_gen = subprocess.Popen([self.openssl, 'ca', '-config',
          self.openssl_config, '-gencrl', '-out', crl], stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT)
        result = crl_gen.communicate()[0]
        if crl_gen.returncode is None or crl_gen.returncode != 0:
          LOG('CertificateAuthorityTool', ERROR, 'Issue during CRL generation, result was:%r' % result)
          crl_gen.kill()
          raise CertificateGenerationError
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
