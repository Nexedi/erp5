#
# Authors : Tarek Ziade tziade@nuxeo.com
#           Robin Sebastien seb@nexedi.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
""" CPS ERP5 Portal
"""

import Globals
from Globals import InitializeClass
from zLOG import LOG, INFO, DEBUG
from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.CMFDefault.Portal import PortalGenerator
from Products.ERP5.ERP5Site import ERP5Generator
from Products.CPSDefault.Portal import CPSDefaultSite
from Products.CMFCore.utils import getToolByName

from Products.ERP5.ERP5Site import ERP5Site

from os import path




manage_addERP5CPSSiteForm = Globals.HTMLFile(
    'zmi/manage_addERP5CPSSite_form',
    globals())

def manage_addERP5CPSSite(dispatcher, id,
                               title='ERP5 CPS Site',
                               description='',
                               langs_list=None,
                               root_id='root',
                               root_sn='CPS',
                               root_givenName='Root',
                               root_email='root@localhost',
                               root_password1='',
                               root_password2='',
                               enable_portal_joining=1,
                               sql_connection_type='Z MySQL Database Connection',
                               sql_connection_string='test test',
                               REQUEST=None):
    """Add a Intranet SN Default Site."""

    _log = []
    def pr(bla, zlog=1, _log=_log):
        if bla == 'flush':
            return '\n'.join(_log)
        _log.append(bla)
        if (bla and zlog):
            LOG('addERP5CPSSite:', INFO, bla)

    if not root_password1:
        raise ValueError, 'You have to fill CPS Administrator password!'

    if root_password1 != root_password2:
        raise ValueError, 'Password confirmation does not match password'

    id = id.strip()
    title = title.strip()
    description = description.strip()
    root_givenName = root_givenName.strip()
    root_sn = root_sn.strip()
    email_from_name = '%s %s' % (root_givenName, root_sn)
    root_email = root_email.strip()

    pr('Adding a ERP5CPS Site')
    gen = ERP5CPSGenerator()
    #portal = gen.create(dispatcher, id, 0,sql_connection_type,sql_connection_string)
    portal = gen.create(dispatcher, id, 0)
    gen.setupDefaultProperties(portal, title, description,
                               email_from_address=root_email,
                               email_from_name=email_from_name,
                               validate_email=0)
    portal.sql_connection_type = sql_connection_type
    portal.sql_connection_string = sql_connection_string

    pr('Creating cpsupdate External Method in CPS Site')
    cpsupdate = ExternalMethod('cpsupdate',
                               'CPSDefault Updater',
                               'CPSDefault.cpsinstall',
                               'cpsupdate')
    portal._setObject('cpsupdate', cpsupdate)

    pr('Creating benchmark External Method')
    benchmarktimer = ExternalMethod('BenchmarkTimer',
                                    'BenchmarkTimer',
                                    'CPSDefault.benchmarktimer',
                                    'BenchmarkTimerInstance')
    portal._setObject('Benchmarktimer', benchmarktimer)

    pr('Creating i18n Updater Support')
    i18n_updater = ExternalMethod('i18n Updater',
                                  'i18n Updater',
                                  'CPSDefault.cpsinstall',
                                  'cps_i18n_update')
    portal._setObject('i18n Updater', i18n_updater)

    pr('Executing CPSDefault Installer')
    pr(portal.cpsupdate(langs_list=langs_list, is_creation=1 ), 0)

    pr('Configuring CPSDefault Site')
    # editProperties do not work with ZTC due to usage of REQUEST
    # to send properties :/
    # herve: REQUEST is a mapping. Have you checked using
    #            REQUEST={'smtp_host': 'localhost'}
    #        as an argument?
    portal.MailHost.smtp_host = 'localhost'
    portal.manage_changeProperties(smtp_server='localhost', REQUEST=None)

    # Launching specific Intranet SN stuffs
    pr('Launching CPS ERP5 Specifics')
    ERP5CPS_installer = ExternalMethod('CPS ERP5 UPDATE',
                                          'CPS ERP5 UPDATE',
                                          'ERP5CPS.install',
                                          'install')
    portal._setObject('ERP5CPS_installer', ERP5CPS_installer)

    pr(portal.ERP5CPS_installer(), 0)

    pr('Done')
    if REQUEST is not None:
        REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')

    return pr('flush')

class ERP5CPSSite(CPSDefaultSite,ERP5Site):
    """CPS ERP5 Site  variant of a CPS Default Site.
    """
    constructors = (manage_addERP5CPSSiteForm, manage_addERP5CPSSite, )
    meta_type = 'ERP5 CPS Site'

    icon = 'portal.gif'

    enable_portal_joining = 0

    _properties = CPSDefaultSite._properties

InitializeClass(ERP5CPSSite)

class ERP5CPSGenerator(PortalGenerator):
    """Set up a CPS Site."""
    klass = ERP5CPSSite

