##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
"""
    ERP5 is a set of components to implement an ERP
    with Zope
"""

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
from AccessControl import ModuleSecurityInfo
import sys, Permissions
this_module = sys.modules[ __name__ ]
document_classes = updateGlobals( this_module, globals(), permissions_module = Permissions)
from Products.PythonScripts.Utility import allow_class

import Selection
allow_class(Selection)

# Define object classes and tools
import Form, FSForm, ListBox, MatrixBox, SelectionTool, ZGDChart, PDFTemplate,\
       Report, PDFForm, ParallelListField
import PlanningBox
import RelationField, ImageField, MultiRelationField
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator import StandardFields, HelperFields
from Products.CMFCore.utils import registerIcon
object_classes = ( Form.ERP5Form, FSForm.ERP5FSForm, PDFTemplate.PDFTemplate, Report.ERP5Report, PDFForm.PDFForm)
portal_tools = ( SelectionTool.SelectionTool,  )
content_classes = ()
content_constructors = ()

# Import patch
import FormulatorPatch

# Optimization
import psyco
psyco.bind(ListBox.ListBoxWidget.render)
psyco.bind(ListBox.ListBoxValidator.validate)
#psyco.bind(Form.ERP5Field.get_value)
#psyco.bind(Form.ERP5Form.__call__)
#psyco.bind(Form.ERP5Form._exec)

# Finish installation
def initialize( context ):
    import Document
    initializeProduct(context, this_module, globals(),
                         document_module = Document,
                         document_classes = document_classes,
                         object_classes = object_classes,
                         portal_tools = portal_tools,
                         content_constructors = content_constructors,
                         content_classes = content_classes)

    # Initialise ERP5Form Formulator
    FieldRegistry.registerField(ListBox.ListBox,
                                'www/StringField.gif')
    FieldRegistry.registerField(PlanningBox.PlanningBox,
                                'www/StringField.gif')
    FieldRegistry.registerField(ZGDChart.ZGDChart,
                                'www/StringField.gif')
    FieldRegistry.registerField(MatrixBox.MatrixBox,
                                'www/StringField.gif')
    FieldRegistry.registerField(RelationField.RelationStringField,
                                'www/StringField.gif')
    FieldRegistry.registerField(MultiRelationField.MultiRelationStringField,
                                'www/StringField.gif')
    FieldRegistry.registerField(ImageField.ImageField,
                                'www/StringField.gif')
    FieldRegistry.registerField(ParallelListField.ParallelListField,
                                'www/StringField.gif')
    FieldRegistry.registerField(StandardFields.StringField,
                                'www/StringField.gif')
    #FieldRegistry.registerField(StandardFields.LabelField,
    #                            'www/LabelField.gif')
    FieldRegistry.registerField(StandardFields.CheckBoxField,
                                'www/CheckBoxField.gif')
    FieldRegistry.registerField(StandardFields.IntegerField,
                                'www/IntegerField.gif')
    FieldRegistry.registerField(StandardFields.TextAreaField,
                                'www/TextAreaField.gif')
    FieldRegistry.registerField(StandardFields.RawTextAreaField,
                                'www/TextAreaField.gif')
    FieldRegistry.registerField(StandardFields.LinesField,
                                'www/LinesField.gif')
    FieldRegistry.registerField(StandardFields.ListField,
                                'www/ListField.gif')
    FieldRegistry.registerField(StandardFields.MultiListField,
                                'www/MultiListField.gif')
    FieldRegistry.registerField(StandardFields.RadioField,
                                'www/RadioField.gif')
    FieldRegistry.registerField(StandardFields.MultiCheckBoxField,
                                'www/MultiCheckBoxField.gif')
    FieldRegistry.registerField(StandardFields.PasswordField,
                                'www/PasswordField.gif')
    FieldRegistry.registerField(StandardFields.EmailField,
                                'www/EmailField.gif')
    FieldRegistry.registerField(StandardFields.PatternField,
                                'www/PatternField.gif')
    FieldRegistry.registerField(StandardFields.FloatField,
                                'www/FloatField.gif')
    FieldRegistry.registerField(StandardFields.DateTimeField,
                                'www/DateTimeField.gif')
    FieldRegistry.registerField(StandardFields.FileField,
                                'www/FileField.gif')
    FieldRegistry.registerField(StandardFields.LinkField,
                                'www/LinkField.gif')

    # some helper fields
    FieldRegistry.registerField(HelperFields.ListTextAreaField)
    FieldRegistry.registerField(HelperFields.MethodField)
    FieldRegistry.registerField(HelperFields.TALESField)

    # register help for the product
    context.registerHelp()
    # register field help for all fields
    FieldRegistry.registerFieldHelp(context)

    # register the form itself
    #context.registerClass(
    #    Form.ZMIForm,
    #    constructors = (Form.manage_addForm,
    #                    Form.manage_add),
    #    icon = 'www/Form.png')

    # make Dummy Fields into real fields
    FieldRegistry.initializeFields()

    # do initialization of Form class to make fields addable
    Form.initializeForm(FieldRegistry)
    Form.initializeForm(FieldRegistry, form_class = Report.ERP5Report)

    # Register FSPDFTemplate icon
    registerIcon(PDFTemplate.FSPDFTemplate,
                        'www/PDF.png', globals())


ModuleSecurityInfo('Products.ERP5Form.Report').declarePublic('ReportSection',)
