## Script (Python) "PaySheetTransaction_initializePreview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
import random
from Products.ERP5Type.Document import newTempBase
from string import zfill

global portal_object, num, l
portal_object = context.getPortalObject()
num = 0
l = []

# get all pre-calculated rates and bases
default_values = context.PaySheetTransaction_preCalculation()

# function to create a new preview line
def createPreviewLine   ( new_id                = None
                        , new_title             = None
                        , new_base              = None
                        , new_base_name         = None
                        , new_employee_rate     = None
                        , new_employer_rate     = None
                        , new_service_url       = None
                        , new_organisation_url  = None
                        , new_salary_range_cat  = None
                        , new_tax_cat           = None
                        ):
    global portal_object, num, l
    num += 1
    int_len = 3
    o = newTempBase(portal_object, new_id)
    o.setUid('new_%s' % zfill(num, int_len))
    o.edit(uid='new_%s' % zfill(num, int_len))
    o.edit  ( id                    = new_id
            , title                 = new_title
            , base                  = new_base
            , base_name             = new_base_name
            , employee_share_rate   = new_employee_rate
            , employer_share_rate   = new_employer_rate
            , service_url           = new_service_url
            , organisation_url      = new_organisation_url
            , salary_range_cat      = new_salary_range_cat
            , tax_cat               = new_tax_cat
            )
    l.append(o)

# get all services related to pay sheet transaction
paysheet_services = []
erp5site = context.portal_url.getPortalObject()
for service in erp5site['service'].objectValues():
    base_cat = service.getVariationRangeBaseCategoryList()
    # a service is related to paysheet transaction if it has 'tax_category' et 'salary_range' as base category
    if 'tax_category' in base_cat and 'salary_range' in base_cat:
        paysheet_services.append(service)

# Sort the service list by id
paysheet_services.sort(lambda x, y: cmp(x.getId(), y.getId()))

# generate all lines for the preview form
for serv in paysheet_services:
    cat_list = serv.getCategoryList()
    # store all categories of the service into lists
    tax_cat     = []
    range_cat   = []
    for cat in cat_list:
        if str(cat).find('tax_category') != -1:
            tax_cat.append(cat)
        if str(cat).find('salary_range') != -1:
            range_cat.append(cat)
    # create a line for every salary_range of the service
    for base in range_cat:
        name = serv.getId() + '/' + context.portal_categories.resolveCategory(base).getId()
        # a preview line is composed of a base calculation, an employee share rate and an employer share rate
        if default_values.has_key(name):
            new_base            = default_values[name]['base']
            new_employee_rate   = default_values[name]['employee_rate']
            new_employer_rate   = default_values[name]['employer_rate']
        # create a preview line for every salary_range value of the service
        createPreviewLine   ( new_id                = serv.getId()
                            , new_title             = serv.getTitleOrId()
                            , new_base              = new_base
                            , new_base_name         =   context.portal_categories.resolveCategory(base).getTitleOrId()
                            , new_employee_rate     = new_employee_rate
                            , new_employer_rate     = new_employer_rate
                            , new_service_url       = serv.getRelativeUrl()
                            , new_organisation_url  = serv.getSource()
                            , new_salary_range_cat  = base
                            , new_tax_cat           = tax_cat
                            )

# return the list of preview lines
return l
