## Script (Python) "PaySheetTransaction_preCalculation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ags_rate=None, industrial_accident_rate=None, transport_payment_rate=None, syntec_rate=None
##title=
##
True  = 1
False = 0

global paysheet
paysheet      = context.getObject()
paysheet_type = paysheet.getPortalType()

employee        = paysheet.getDestinationSection()
employee_object = paysheet.getDestinationSectionValue()
employer        = paysheet.getSourceSection()
employer_object = paysheet.getSourceSectionValue()


gross_salary = abs(paysheet.getGrossSalary())

# check if the employee is executive or not
if employee_object.getCareerGrade().split('/')[-1:][0] in ('engineer'):
  executive = True
else:
  executive = False

company_birth = employer_object.getCreationDate()

employer_region = employer_object.getDefaultAddress().getZipCode()[:2]

# get the number of person which are employed by the company ,
# sub_list = employer_object.getSubordinationRelatedValueList()
# company_size = 0
# for person in sub_list:
#   if person.getPortalType() == 'Person': # add condition: if current role == internal and defaultCareerEnd and defaultCareerStart fit in the current year
#     #print repr(person) + repr(person.getTitle())
#     company_size += 1
#
# print repr(company_size)
#
# return printed

company_size = 3


# limited salary = salaire plafonné
if gross_salary < 2432:     #!!! depending of the wage periodicity, 2432 euros is for a month
  limited_salary = gross_salary
else:
  limited_salary = 2432

# "Char" slice type
slice_a_value = 2432
slice_b_value = 9728
slice_c_value = 19456
char_slices = {}
if gross_salary < slice_a_value:
    char_slices['A'] = gross_salary
else:
    char_slices['A'] = slice_a_value
    if gross_salary < slice_b_value:
        char_slices['B'] = float(gross_salary) - float(slice_a_value)
    else:
        char_slices['B'] = slice_b_value
        if gross_salary < slice_c_value:
            char_slices['C'] = float(gross_salary) - float(slice_b_value)
        else:
            char_slices['C'] = slice_c_value

# "Number" slice type
slice_1_value = 2432
slice_2_value = 7296
num_slices = {}
if gross_salary < slice_1_value:
    char_slices['1'] = gross_salary
else:
    char_slices['1'] = slice_1_value
    if gross_salary < slice_2_value:
        char_slices['2'] = gross_salary - slice_1_value
    else:
        char_slices['2'] = slice_2_value

# age-slice of the company
old_limit = DateTime(1997, 1, 1)
if company_birth < old_limit:
  comp_type = 'old'
else:
  comp_type = 'new'


#################
# This script will fill the PaySheetTransaction_preview with default values for base salary calculation, employer and employee share
#################

default = {}
# initialize all variables to None
paysheet_services = []
erp5site = context.portal_url.getPortalObject()
for service in erp5site['service'].objectValues():
    base_cat = service.getVariationRangeBaseCategoryList()
    if 'tax_category' in base_cat and 'salary_range' in base_cat:
        paysheet_services.append(service)
for serv in paysheet_services:
    cat_list = serv.getCategoryList()
    tax_cat = []
    range_cat = []
    for cat in cat_list:
        if str(cat).find('tax_category') != -1:
            tax_cat.append(cat)
        if str(cat).find('salary_range') != -1:
            range_cat.append(cat)
    for base in range_cat:
        new_name = serv.getId() + '/' + context.portal_categories.resolveCategory(base).getId()
        default[new_name] = {'employer_rate':None,'employee_rate':None,'base':None}

# sickness insurance
if employer_region in ('57', '67', '68'):
    er = 1.70
else:
    er = 0.75
default['sickness_insurance/salaire_brut'] = \
{ 'employer_rate' : 12.80
, 'employee_rate' : er
, 'base'          : gross_salary
}

# old-age insurance
default['oldage_insurance/salaire_brut'] = \
{ 'employer_rate'          : 1.60
, 'employee_rate'          : None
, 'base'        : gross_salary
}
default['oldage_insurance/salaire_plafonne'] = \
{ 'employer_rate'  : 8.20
, 'employee_rate'  : 6.55
, 'base': limited_salary
}

# widowhood insurance
default['widowhood_insurance/salaire_brut'] = \
{ 'employer_rate'          : None
, 'employee_rate'          : 0.10
, 'base'        : gross_salary
}

# family benefits
default['family_benefits/salaire_brut'] = \
{ 'employer_rate'          : 5.40
, 'employee_rate'          : None
, 'base'        : gross_salary
}

# industrial accident
# industrial_accident_rate is a parameter of this script, because rate depending of company size, department & trade (1.10 is for Nexedi, 1.0 is the default value)
if industrial_accident_rate in ('', 0, None):
    industrial_accident_rate = 1.0
default['industrial_accident/salaire_brut'] = \
{ 'employer_rate'          : industrial_accident_rate
, 'employee_rate'          : None
, 'base'        : gross_salary
}

# lodging helps
if company_size > 9:
    default['lodging_helps/salaire_brut'] = \
    { 'employer_rate'          : 0.40
    , 'employee_rate'          : None
    , 'base'        : gross_salary
    }
else:
    default['lodging_helps/salaire_plafonne'] = \
    { 'employer_rate'  : 0.10
    , 'employee_rate'          : None
    , 'base': limited_salary
    }

# transport payment
# TODO: rate depending of the town, 1.80 is the 'default' value (when the town isn't referenced by laws)
if transport_payment_rate in ('', 0, None):
    transport_payment_rate = 1.80
if company_size > 9:
    default['transport_payment/salaire_brut'] = \
    { 'employer_rate'          : transport_payment_rate
    , 'employee_rate'          : None
    , 'base'        : gross_salary
    }

# CSG
default['csg_deductible/salaire_brut_csg'] = \
{ 'employer_rate'      :None
, 'employee_rate'          :5.10
, 'base'    : 0.95 * gross_salary
}
default['csg_non_deductible/salaire_brut_csg'] = \
{ 'employer_rate'      :None,
 'employee_rate'      : 2.4
, 'base'    : 0.95 * gross_salary
}

# CRDS
default['crds/salaire_brut_crds'] = \
{ 'employer_rate':None,
'employee_rate'     : 0.50
, 'base'   : 0.95 * gross_salary
}

# unemployment insurance
if char_slices.has_key('A'):
    default['unemployment_insurance/tranche_a']['employer_rate']     = 4.0
    default['unemployment_insurance/tranche_a']['employee_rate']     = 2.4
    default['unemployment_insurance/tranche_a']['base']   = char_slices['A']
if char_slices.has_key('B'):
    default['unemployment_insurance/tranche_b']['employer_rate']     = 4.0
    default['unemployment_insurance/tranche_b']['employee_rate']     = 2.4
    default['unemployment_insurance/tranche_b']['base']   = char_slices['B']

# AGS
# ags_rate is a parameter of this script, 0.35% was the default value, now it's 0.45%
if ags_rate in ('', 0, None):
    ags_rate = 0.45
if char_slices.has_key('A'):
    default['ags/tranche_a']['employer_rate']      = ags_rate
    default['ags/tranche_a']['base']    = char_slices['A']
if char_slices.has_key('B'):
    default['ags/tranche_b']['employer_rate']      = ags_rate
    default['ags/tranche_b']['base']    = char_slices['B']

# ARRCO
if executive == False:
    if num_slices.has_key('1'):
        default['arrco/tranche_1']['employer_rate']    = 4.5
        default['arrco/tranche_1']['employee_rate']    = 3.0
        default['arrco/tranche_1']['base']  = num_slices['1']
    if num_slices.has_key('2'):
        if comp_type == 'old':
            employee_share_rate   = 6.0
            employer_share_rate = 9.0
        else:
            employee_share_rate   = 8.0
            employer_share_rate = 12.0
        default['arrco/tranche_2']['employer_rate']    = employer_share_rate
        default['arrco/tranche_2']['employee_rate']    = employee_share_rate
        default['arrco/tranche_2']['base']  = num_slices['2']
elif char_slices.has_key('A'):
    default['arrco/tranche_a']['employer_rate']    = 4.5
    default['arrco/tranche_a']['employee_rate']    = 3.0
    default['arrco/tranche_a']['base']  = char_slices['A']

# AGFF
if executive == True:
    if char_slices.has_key('A'):
        default['agff/tranche_a']['employer_rate']     = 1.20
        default['agff/tranche_a']['employee_rate']     = 0.80
        default['agff/tranche_a']['base']   = char_slices['A']
    if char_slices.has_key('B'):
        default['agff/tranche_b']['employer_rate']     = 1.30
        default['agff/tranche_b']['employee_rate']     = 0.90
        default['agff/tranche_b']['base']   = char_slices['B']
else:
    if num_slices.has_key('1'):
        default['agff/tranche_1']['employer_rate']     = 1.20
        default['agff/tranche_1']['employee_rate']     = 0.80
        default['agff/tranche_1']['base']   = num_slices['1']
    if num_slices.has_key('2'):
        default['agff/tranche_2']['employer_rate']     = 1.30
        default['agff/tranche_2']['employee_rate']     = 0.90
        default['agff/tranche_2']['base']   = num_slices['2']

# AGIRC
# TODO: fix the repartition of share rate in case of slice C
if executive == True:
    if char_slices.has_key('B'):
        default['agirc/tranche_b']['employer_rate']    = 12.50
        default['agirc/tranche_b']['employee_rate']    = 7.50
        default['agirc/tranche_b']['base']  = char_slices['B']
    if char_slices.has_key('C'):
        # free repartition (20% to share between employee & employer)
        default['agirc/tranche_b']['employer_rate']    = 10.00
        default['agirc/tranche_b']['employee_rate']    = 10.00
        default['agirc/tranche_b']['base']  = char_slices['C']

# CET
if executive == True:
    if char_slices.has_key('A'):
        default['cet/tranche_a']['employer_rate']    = 0.22
        default['cet/tranche_a']['employee_rate']    = 0.13
        default['cet/tranche_a']['base']  = char_slices['A']
    if char_slices.has_key('B'):
        default['cet/tranche_b']['employer_rate']    = 0.22
        default['cet/tranche_b']['employee_rate']    = 0.13
        default['cet/tranche_b']['base']  = char_slices['B']
    if char_slices.has_key('C'):
        default['cet/tranche_c']['employer_rate']    = 0.22
        default['cet/tranche_c']['employee_rate']    = 0.13
        default['cet/tranche_c']['base']  = char_slices['C']

# life insurance
if executive == True and char_slices.has_key('A'):
    default['life_insurance/tranche_a'] = \
    { 'employer_rate'      : 1.5
    , 'employee_rate': None
    , 'base'    : char_slices['A']
    }

# APEC
if char_slices.has_key('B'):
    default['apec/tranche_b'] = \
    { 'employer_rate'      : 0.036
    , 'employee_rate'      : 0.024
    , 'base'    : char_slices['B']
    }

# construction tax
if company_size > 9:
    default['construction_tax/salaire_brut'] = \
    { 'employer_rate'      : 0.45
    , 'employee_rate': None
    , 'base'    : gross_salary
    }

# training tax
default['training_tax/salaire_brut'] = \
{ 'employer_rate'      : 0.50
, 'employee_rate': None
, 'base'    : gross_salary
}

# courses tax
if company_size < 10:
    rate = 0.15
else:
    rate = 1.5
default['courses_tax/salaire_brut'] = \
{ 'employer_rate'      : rate
, 'employee_rate':None
, 'base'    : gross_salary
}

# Syntec convention
#syntec_rate = 0.915
# XXX If it is the paysheet of yoshinory , we do *2 because he is married.
# if married(employee) : syntec_rate = syntec_rate * 2
#syntec_rate = 1.83
if syntec_rate in ('', 0, None):
    syntec_rate = 0.915
default['syntec_insurance/salaire_plafonne_syntec'] = \
{ 'employer_rate'   : syntec_rate
, 'employee_rate'   : syntec_rate
, 'base' : 2432
}

return default
