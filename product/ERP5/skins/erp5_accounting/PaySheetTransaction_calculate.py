## Script (Python) "PaySheetTransaction_calculate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# TODO: "#!!!" style comment
# o replace etat by right organism

True  = 1
False = 0

pay_sheet           = context.getObject()
pay_sheet_type      = pay_sheet.getPortalType()
pay_sheet_line_type = pay_sheet_type + ' Line'
employee            = pay_sheet.getDestinationSection()
employer            = pay_sheet.getSourceSection()
employer_object     = pay_sheet.getSourceSectionValue()

# social organism
org_urssaf  = 'organisation/urssaf'
org_assedic = 'organisation/assedic'
org_arrco   = 'organisation/arrco'
org_agff    = 'organisation/agff'
org_agirc   = 'organisation/agirc'
org_apec    = 'organisation/apec'
org_etat    = 'organisation/etat'

# gross salary source and destination
charge_salariale = 'account/charges_salariales'
produit_salarial = 'account/produits_salariales'

# final salary source and destination
dette_salarie   = 'account/dettes_salaries'
creance_salarie = 'account/creances_salaries'

# employer share source and destination
charge_sociale = 'account/charges_sociales'
produit_social = 'account/produits_sociaux'

# employer + employee share source and destination
dette_sociale   = 'account/dettes_sociales'
creance_sociale = 'account/creances_sociales'



### get the gross salary and other basic informations to calculate the paysheet

gross_salary = abs(pay_sheet.getGrossSalary())
#pay_sheet_resource = pay_sheet.getCurrency()   why it doesn't work ?????
pay_sheet_resource = 'currency/EUR'

global salary_share_total
salary_share_total = 0.0

executive = True                      ################### #!!! dynamic get

company_birth = DateTime(2000, 10, 21)

employer_region = employer_object.getDefaultAddress().getZipCode()[:2]

sub_list = employer_object.getSubordinationRelatedValueList()
company_size = 0
for person in sub_list:
  if person.getPortalType() == 'Person':
    company_size += 1

company_size = 3

### define some parameters for the calculation

# ceiling salary
if gross_salary < 2432:     #!!! depending of the wage periodicity, 2432 euros is for a month
  ceiling_salary = gross_salary
else:
  ceiling_salary = 2432

# "Char" slice type
if gross_salary <= 2432:
  char_slice = 'A'
elif gross_salary <= 9728:
  char_slice = 'B'
elif gross_salary <= 19456:
  char_slice = 'C'
else:
  char_slice = ''

# "Number" slice type
if gross_salary <= 2432:
  num_slice = 1
elif gross_salary <= 7296:
  num_slice = 2
else:
  num_slice = 0

# age-slice of the company
old_limit = DateTime(1997, 1, 1)
if company_birth < old_limit:
  comp_type = 'old'
else:
  comp_type = 'new'



### create a new pay sheet line
def createPaySheetLine(new_id='', new_title='', share='',
                       src_sec='', src='', src_deb=None,
                       dest_sec='', dest='', new_desc=''):

  suffix = {'cs': '',
            'pp': ' (part patronale)'}
  if share == 'pp' or share == 'cs':
    new_id = string.replace(string.lower(new_title), ' ', '_')
    new_id += '_' + share
    #new_title = string.replace(new_title, '?', 'e')
    #new_title = string.replace(new_title, '?', 'e')
    #new_title = string.replace(new_title, '?', 'o')
    new_title += suffix[share]
    if share == 'cs':
      src_sec  = employer
      src      = dette_sociale
      dest     = creance_sociale
    elif share == 'pp':
      src_sec  = employer
      src      = charge_sociale
      dest     = produit_social
  #if wrong ID (existing or wrong name): new_id = str(pay_sheet.generateNewId())
  context.portal_types.constructContent(type_name = pay_sheet_line_type,
                                        container = pay_sheet,
                                        id        = new_id)
  pay_sheet[new_id].setTitle(new_title)
  pay_sheet[new_id].setResource(pay_sheet_resource)  # default currency
  pay_sheet[new_id].setSourceSection(src_sec)
  pay_sheet[new_id].setSource(src)
  pay_sheet[new_id].setDestinationSection(dest_sec)
  pay_sheet[new_id].setDestination(dest)
  pay_sheet[new_id].setSourceDebit(src_deb)
  pay_sheet[new_id].setSourceDebit(src_deb)
  pay_sheet[new_id].setDescription(new_desc)



### add a pay sheet item and manage the accounting writing rules
def addPaySheetItem(title='', values={'salary_share_rate':None, 'employer_share_rate':None, 'base_value':None, 'base_description':None}, dest_org=''):
    global salary_share_total
    salary_share_value = None
    employer_share_value = None
    ps_description = None
    pp_description = None
    if values['salary_share_rate']!=None and values['base_value']!=None:
        salary_share_value = (float(values['salary_share_rate']) / 100) * values['base_value']
        ps_description = "= " + str(values['salary_share_rate']) + "% * " + str(values['base_value']) + " (=" + str(values['base_description']) + ")"
    if values['employer_share_rate']!=None and values['base_value']!=None:
        employer_share_value = (float(values['employer_share_rate']) / 100) * values['base_value']
        pp_description = "= " + str(values['employer_share_rate']) + "% * " + str(values['base_value']) + " (=" + str(values['base_description']) + ")"
    if salary_share_value == None and employer_share_value == None:
        return
    if salary_share_value != None:
        salary_share_total += float(salary_share_value)
    if employer_share_value == None:
        createPaySheetLine( new_title = title,
                            share     = 'cs',
                            src_deb   = salary_share_value,
                            dest_sec  = dest_org,
                            new_desc  = ps_description)
        return
    if salary_share_value == None:
        createPaySheetLine( new_title = title,
                            share     = 'cs',
                            src_deb   = employer_share_value,
                            dest_sec  = dest_org,
                            new_desc  = ps_description)
        createPaySheetLine( new_title = title,
                            share     = 'pp',
                            src_deb   = employer_share_value,
                            dest_sec  = dest_org,
                            new_desc  = pp_description)
        return
    createPaySheetLine( new_title = title,
                        share     = 'cs',
                        src_deb   = float(employer_share_value) + float(salary_share_value),
                        dest_sec  = dest_org,
                        new_desc  = ps_description)
    createPaySheetLine( new_title = title,
                        share     = 'pp',
                        src_deb   = employer_share_value,
                        dest_sec  = dest_org,
                        new_desc  = pp_description)



### add the gross salary Pay Sheet Line
createPaySheetLine( new_id      = 'gs',
                    new_title   = 'Salaire brut',
                    src_sec     = employer,
                    src         = charge_salariale,
                    src_deb     = gross_salary,
                    dest_sec    = employee,
                    dest        = produit_salarial)



### Social Security
# sickness insurance
sickness_insurance =    { 'salary_share_rate'   : None
                        , 'employer_share_rate' : 12.80
                        , 'base_value'          : gross_salary
                        , 'base_description'    : "salaire brut"
                        }
if employer_region == '57' or employer_region == '67' or employer_region == '68':
    sickness_insurance['salary_share_rate'] = 1.70
else:
    sickness_insurance['salary_share_rate'] = 0.75
addPaySheetItem(title       = 'Assurance maladie',
                values      = sickness_insurance,
                dest_org    = org_urssaf)

# old-age insurance
# this contribution is special because salary and employer shares are calculated from 2 base
# salary_share_value = (6.55 / 100) * ceiling_salary
# salary_share_total += float(salary_share_value)
# ps_description = "= 6.55% * " + str(ceiling_salary) + " (=salaire plafonné)"
# employer_share_value = gross_salary * (1.60 / 100) + ceiling_salary * (8.20 / 100)
# pp_description = "= 1.60% * " + str(gross_salary) + " + 8.20% * " + str(ceiling_salary) + " = 1.60% * salaire brut + 8.20% * salaire plafonné"
# createPaySheetLine( new_title = 'Assurance vieillesse',
#                     share     = 'cs',
#                     src_deb   = float(employer_share_value) + float(salary_share_value),
#                     dest_sec  = org_urssaf,
#                     new_desc  = ps_description)
# createPaySheetLine( new_title = 'Assurance vieillesse',
#                     share     = 'pp',
#                     src_deb   = employer_share_value,
#                     dest_sec  = org_urssaf,
#                     new_desc  = pp_description)
oldage_insurance1 = { 'salary_share_rate'   : None
                    , 'employer_share_rate' : 1.60
                    , 'base_value'          : gross_salary
                    , 'base_description'    : "salaire brut"
                    }
addPaySheetItem(title    = 'Assurance vieillesse 1',
                values   = oldage_insurance1,
                dest_org = org_urssaf)
oldage_insurance2 = { 'salary_share_rate'   : 6.55
                    , 'employer_share_rate' : 8.20
                    , 'base_value'          : ceiling_salary
                    , 'base_description'    : "salaire plafonné"
                    }
addPaySheetItem(title    = 'Assurance vieillesse 2',
                values   = oldage_insurance2,
                dest_org = org_urssaf)
# widowhood insurance
widowhood_insurance =   { 'salary_share_rate'   : 0.10
                        , 'employer_share_rate' : None
                        , 'base_value'          : gross_salary
                        , 'base_description'    : "salaire brut"
                        }
addPaySheetItem(title    = 'Assurance veuvage',
                values   = widowhood_insurance,
                dest_org = org_urssaf)
# family benefits
family_benefits =   { 'salary_share_rate'   : None
                    , 'employer_share_rate' : 5.40
                    , 'base_value'          : gross_salary
                    , 'base_description'    : "salaire brut"
                    }
addPaySheetItem(title       = 'Allocations familiales',
                values      = family_benefits,
                dest_org    = org_urssaf)
# industrial accident
industrial_accident =   { 'salary_share_rate'   : None
                        , 'employer_share_rate' : 1.10  # rate depending of company size, department & trade; 1.0 as standard rate, 1.1 for IT
                        , 'base_value'          : gross_salary
                        , 'base_description'    : "salaire brut"
                        }
addPaySheetItem(title    = 'Accidents du travail',
                values   = industrial_accident,
                dest_org = org_urssaf)
# lodging helps
lodging_helps = { 'salary_share_rate'   : None
                , 'employer_share_rate' : None
                , 'base_value'          : None
                , 'base_description'    : None
                }
if company_size > 9:
    lodging_helps['employer_share_rate'] = 0.40
    lodging_helps['base_description'] = "salaire brut"
    lodging_helps['base_value'] = gross_salary
else:
    lodging_helps['employer_share_rate'] = 0.10
    lodging_helps['base_description'] = "salaire plafonné"
    lodging_helps['base_value'] = ceiling_salary
addPaySheetItem(title    = 'Aide au logement',
                values   = lodging_helps,
                dest_org = org_urssaf)
# transport payment
if company_size > 9:
    transport_payment = { 'salary_share_rate'   : None
                        , 'employer_share_rate' : 1.80     # rate depending of the town
                        , 'base_value'          : gross_salary
                        , 'base_description'    : "salaire brut"
                        }
    addPaySheetItem(title       = 'Versement au transport',
                    values      = transport_payment,
                    dest_org    = org_urssaf)



### CSG = Contribution Sociale Generalisee (deductible / non deductible)
CSGd =  { 'salary_share_rate'   : 2.4
        , 'employer_share_rate' : None
        , 'base_value'          : 0.95 * gross_salary
        , 'base_description'    : "95% du salaire brut"
        }
addPaySheetItem(title    = 'CSG deductible',
                values   = CSGd,
                dest_org = org_urssaf)
CSGnd = { 'salary_share_rate'   : 5.1
        , 'employer_share_rate' : None
        , 'base_value'          : 0.95 * gross_salary
        , 'base_description'    : "95% du salaire brut"
        }
addPaySheetItem(title    = 'CSG non deductible',
                values   = CSGnd,
                dest_org = org_urssaf)



### CRDS = Contribution pour le Remboursement de la Dette Sociale
CRDS =  { 'salary_share_rate'   : 0.5
        , 'employer_share_rate' : None
        , 'base_value'          : 0.95 * gross_salary
        , 'base_description'    : "95% du salaire brut"
        }
addPaySheetItem(title    = 'CRDS',
                values   = CRDS,
                dest_org = org_urssaf)



### Unemployment Insurance
if char_slice == 'A' or char_slice == 'B':
    unemployment_insurance =    { 'salary_share_rate'   : 2.4
                                , 'employer_share_rate' : 4.0
                                , 'base_value'          : gross_salary
                                , 'base_description'    : "salaire brut"
                                }
    addPaySheetItem(title    = 'Assurance chomage',
                    values   = unemployment_insurance,
                    dest_org = org_assedic)



### AGS (FNGS)
if char_slice == 'A' or char_slice == 'B':
    AGS =   { 'salary_share_rate'   : None
            , 'employer_share_rate' : 0.35
            , 'base_value'          : gross_salary
            , 'base_description'    : "salaire brut"
            }
    addPaySheetItem(title    = 'AGS',
                    values   = AGS,
                    dest_org = org_assedic)



### supplementary pension
# ARRCO
ARRCO = { 'salary_share_rate'   : None
        , 'employer_share_rate' : None
        , 'base_value'          : gross_salary
        , 'base_description'    : "salaire brut"
        }
if executive == False:
    if num_slice == 1:
        ARRCO['salary_share_rate']   = 3.0
        ARRCO['employer_share_rate'] = 4.5
    elif num_slice == 2:
        if comp_type == 'old':
            ARRCO['salary_share_rate']   = 6.0
            ARRCO['employer_share_rate'] = 9.0
        else:
            ARRCO['salary_share_rate']   = 8.0
            ARRCO['employer_share_rate'] = 12.0
elif char_slice == 'A':
    ARRCO['salary_share_rate']   = 3.0
    ARRCO['employer_share_rate'] = 4.5
addPaySheetItem(title    = 'ARRCO',
                values   = ARRCO,
                dest_org = org_arrco)
# AGFF
AGFF =  { 'salary_share_rate'   : None
        , 'employer_share_rate' : None
        , 'base_value'          : gross_salary
        , 'base_description'    : "salaire brut"
        }
if ((executive == False and num_slice == 1) or
    (executive == True and char_slice == 'A')):
    AGFF['salary_share_rate']   = 0.80
    AGFF['employer_share_rate'] = 1.20
elif ((executive == False and num_slice == 2) or
      (executive == True and char_slice == 'B')):
    AGFF['salary_share_rate']   = 0.90
    AGFF['employer_share_rate'] = 1.30
addPaySheetItem(title    = 'AGFF',
                values   = AGFF,
                dest_org = org_agff)
# AGIRC
if executive == True:
    AGIRC = { 'salary_share_rate'   : None
            , 'employer_share_rate' : None
            , 'base_value'          : gross_salary
            , 'base_description'    : "salaire brut"
            }
    if char_slice == 'B':
        AGIRC['salary_share_rate']   = 7.50
        AGIRC['employer_share_rate'] = 12.50
    elif char_slice == 'C':
        # free repartition (20% to share between employee & employer)
        AGIRC['salary_share_rate']   = 10.0
        AGIRC['employer_share_rate'] = 10.0
    addPaySheetItem(title    = 'AGIRC',
                    values   = AGIRC,
                    dest_org = org_agirc)
# CET
if executive == True and (char_slice == 'A' or char_slice == 'B' or char_slice == 'C'):
    CET =   { 'salary_share_rate'   : 0.13
            , 'employer_share_rate' : 0.22
            , 'base_value'          : gross_salary
            , 'base_description'    : "salaire brut"
            }
    addPaySheetItem(title    = 'CET',
                    values   = CET,
                    dest_org = org_agirc)



### life insurance
if executive == True and char_slice == 'A':
    life_insurance =    { 'salary_share_rate'   : None
                        , 'employer_share_rate' : 1.5
                        , 'base_value'          : gross_salary
                        , 'base_description'    : "salaire brut"
                        }
    addPaySheetItem(title    = 'Assurance deces',
                    values   = life_insurance,
                    dest_org = org_urssaf)



### APEC
if char_slice == 'B':
    APEC =  { 'salary_share_rate'   : 0.024
            , 'employer_share_rate' : 0.036
            , 'base_value'          : gross_salary
            , 'base_description'    : "salaire brut"
            }
    #!!! verifier l'application de cette histoire de forfait...
    #if executive == True and DateTime.Date.Today().month == 3:
    #  apec['s'] = apec['s'] + 7.0
    #  apec['e'] = apec['e'] + 10.51
    addPaySheetItem(title    = 'APEC',
                    values   = APEC,
                    dest_org = org_apec)



### Taxes
# construction tax
if company_size > 9:
    construction_tax =  { 'salary_share_rate'   : None
                        , 'employer_share_rate' : 0.45
                        , 'base_value'          : gross_salary
                        , 'base_description'    : "salaire brut"
                        }
    addPaySheetItem(title    = 'Construction',
                    values   = construction_tax,
                    dest_org = org_etat)
# training tax
training_tax =  { 'salary_share_rate'   : None
                , 'employer_share_rate' : 0.50
                , 'base_value'          : gross_salary
                , 'base_description'    : "salaire brut"
                }
addPaySheetItem(title    = 'Apprentissage',
                values   = training_tax,
                dest_org = org_etat)
# courses tax
courses_tax =   { 'salary_share_rate'   : None
                , 'employer_share_rate' : None
                , 'base_value'          : gross_salary
                , 'base_description'    : "salaire brut"
                }
if company_size < 10:
    courses_tax['employer_share_rate'] = 0.15
else:
    courses_tax['employer_share_rate'] = 1.5
addPaySheetItem(title    = 'Formation professionnelle',
                values   = courses_tax,
                dest_org = org_etat)



### Take Home salary
final_salary = gross_salary - salary_share_total
createPaySheetLine(new_id    = 'final_salary',
                   new_title = 'Salaire Net',
                   src_sec   = employer,
                   src       = dette_salarie,
                   src_deb   = final_salary,
                   dest_sec  = employee,
                   dest      = creance_salarie)
