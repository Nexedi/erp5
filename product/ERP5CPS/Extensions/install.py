#!/usr/bin/python
#
# Authors : Tarek Ziade tziade@nuxeo.com
#           Robin Sebastien seb@nexedi.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# # by the Free Software Foundation.
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

"""
ERP5CPS Installer

HOWTO USE THAT ?

 - Log into the ZMI as manager
 - Go to your CPS root directory
 - Create an External Method with the following parameters:

     id    : ERP5CPS INSTALLER (or whatever)
     title : ERP5CPS INSTALLER (or whatever)
     Module Name   :  ERP5CPS.install
     Function Name : install
 - save it
 - click now the test tab of this external method.
"""

import sys, os
from zLOG import  LOG,INFO,DEBUG,TRACE
from OFS.ObjectManager import BadRequestException, BadRequest
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION

from Products.CPSCore.CPSWorkflow import TRANSITION_BEHAVIOR_PUBLISHING
from Products.CPSInstaller.CPSInstaller import CPSInstaller
from Products.ERP5.ERP5Site import ERP5Site
from Products.ERP5.ERP5Site import ERP5Generator
from Products.ERP5CPS.ERP5CPSSite import ERP5CPSGenerator
from Products.ERP5CPS import ERP5CPSBoxes
from Products.CMFCore.utils import getToolByName
from os import path


SECTIONS_ID = 'sections'
WORKSPACES_ID = 'workspaces'



SKINS = { 'erp5cps_default': 'Products/ERP5CPS/skins/erp5cps_default',
          'erp5cps_style': 'Products/ERP5CPS/skins/erp5cps_style',
          'erp5cps_images': 'Products/ERP5CPS/skins/erp5cps_images',
          'pro': 'Products/ERP5/skins/pro',
          'erp5': 'Products/ERP5/skins/erp5',
          'activity': 'Products/CMFActivity/skins/activity',
          }


class ERP5CPSInstaller(CPSInstaller,ERP5Generator):
    """ERP5 CPS installer class definition
    """
    product_name = 'ERP5CPS'

    def log(self,message):
        CPSInstaller.log(self,message)
        LOG('ERP5CPSInstaller',INFO,message)

    def install(self):
        """Main call
        """
        self.log("Starting ERP5CPS specific install")
        self.updateCPS()
        self.verifySkins(SKINS)
        self.defineSkins()
        self.setupTranslations()
        self.installMandatoryProducts()
        self.installTreeLoader()
        self.setupBoxes()
        self.finalize()
        #self.reindexCatalog()
        self.installERP5()

        self.log("End of specific ERP5CPS install")

    def updateCPS(self):
        """Update CPS
        """
        self.portal.cpsupdate()

    def defineSkins(self):
        """check skin order for ERP5/CPS compatibility
        """
        portal_skin = getattr(self.portal,'portal_skins')
        layers = portal_skin.selections


        for key in layers.keys():
            selection = layers[key]
            position = selection.find('pro')
            if position >= 0:
                splitted = selection.split(', ')
                try:
                    index_pos = splitted.index('pro')
                except:
                    raise str(splitted)
                del(splitted[index_pos])
                splitted.append('pro')
                selection = ', '.join(splitted)
                layers[key] = selection


    def installERP5(self):
        """
        Install ERP5
        """
        gen = ERP5Generator()
        gen.setupTools(self.portal)
        gen.setupBusinessTemplate(self.portal)

    def installProduct(self,ModuleName,
        InstallModuleName='install',MethodName='install'):
        """ creates an external method for a
            product install and launches it
        """
        objectName ="cpserp5_"+ModuleName+"_installer"

        objectName = objectName.lower()


        # Install the product
        self.log(ModuleName+" INSTALL [ START ]")
        installer = ExternalMethod(objectName,
                                   "",
                                   ModuleName+"."+InstallModuleName,
                                   MethodName)
        try:
            self.portal._setObject(objectName,installer)

        except BadRequestException:
            self.log("External Method for "+ModuleName+" already installed")

        method_link = getattr(self.portal,objectName)

        method_link()

        self.log(ModuleName+" INSTALL [ STOP ]")


    def installMandatoryProducts(self):
        """Installs the mandatory products for ERP5CPS
        """
        pass
        # Installing required products



    def installTreeLoader(self):
        """Install tree loader
        """
        if 'loadTree' not in self.portal.objectIds():
            self.log("  Adding loadTree")
            loadTree = ExternalMethod('loadTree',
                                      'loadTree',
                                      'CPSDefault.loadTree',
                                          'loadTree')
            self.portal._setObject('loadTree', loadTree)
            self.log("  Protecting loadTree")
            self.portal.loadTree.manage_permission(
                'View', roles=['Manager'], acquire=0
                )
            self.portal.loadTree.manage_permission(
                'Access contents information', roles=['Manager'], acquire=0
                )

    def setupBoxes(self):
        """Setup Boxes
        """

        self.log("Adding ERP5CPS default boxes")
        idbc = self.portal.portal_boxes.getBoxContainerId(self.portal)

        self.log("Checking /%s" % idbc )

        if idbc not in self.portal.objectIds():
            self.log("   Creating")
            self.portal.manage_addProduct['CPSDefault'].addBoxContainer()

        # importing boxes
        boxes = ERP5CPSBoxes.getBoxes()
        guard_boxes = ERP5CPSBoxes.getGuardBoxes()

        ttool = self.portal.portal_types

        box_container = self.portal[idbc]

        existing_boxes = box_container.objectIds()

        for box in boxes.keys():
            if box not in existing_boxes:
                self.log("Creation of box: %s" % box)
                apply(ttool.constructContent,
                    (boxes[box]['type'], box_container,
                    box, None), {})
                ob = getattr(box_container, box)
                ob.manage_changeProperties(**boxes[box])
            else:
                ob = getattr(box_container, box)

            # defining guards
            if guard_boxes.has_key(box):
                guard_box = guard_boxes[box]
                self.log("Setting up guards for box: %s" % box)
                ob.setGuardProperties(guard_box)



def install(self):
    installer = ERP5CPSInstaller(self)
    installer.install()
    return installer.logResult()
