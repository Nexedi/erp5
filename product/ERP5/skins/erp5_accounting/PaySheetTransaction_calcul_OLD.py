## Script (Python) "PaySheetTransaction_calcul_OLD"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=agff_slice_1_base=None, agff_slice_1_er=None, agff_slice_1_sr=None, agff_slice_2_base=None, agff_slice_2_er=None, agff_slice_2_sr=None, agff_slice_a_base=None, agff_slice_a_er=None, agff_slice_a_sr=None, agff_slice_b_base=None, agff_slice_b_er=None, agff_slice_b_sr=None, agirc_slice_b_base=None, agirc_slice_b_er=None, agirc_slice_b_sr=None, agirc_slice_c_base=None, agirc_slice_c_er=None, agirc_slice_c_sr=None, ags_slice_a_base=None, ags_slice_a_er=None, ags_slice_b_base=None, ags_slice_b_er=None, apec_slice_b_base=None, apec_slice_b_er=None, apec_slice_b_sr=None, arrco_slice_1_base=None, arrco_slice_1_er=None, arrco_slice_1_sr=None, arrco_slice_2_base=None, arrco_slice_2_er=None, arrco_slice_2_sr=None, arrco_slice_a_base=None, arrco_slice_a_er=None, arrco_slice_a_sr=None, cet_slice_a_base=None, cet_slice_a_er=None, cet_slice_a_sr=None, cet_slice_b_base=None, cet_slice_b_er=None, cet_slice_b_sr=None, cet_slice_c_base=None, cet_slice_c_er=None, cet_slice_c_sr=None, construction_tax_base=None, construction_tax_er=None, courses_tax_base=None, courses_tax_er=None, crds_base=None, crds_sr=None, csg_deductible_base=None, csg_deductible_sr=None, csg_non_deductible_base=None, csg_non_deductible_sr=None, family_benefits_base=None, family_benefits_er=None, industrial_accident_base=None, industrial_accident_er=None, life_insurance_slice_a_base=None, life_insurance_slice_a_er=None, lodging_helps_base=None, lodging_helps_er=None, lodging_helps_limited_base=None, lodging_helps_limited_er=None, oldage_insurance_base=None, oldage_insurance_er=None, oldage_insurance_limited_base=None, oldage_insurance_limited_er=None, oldage_insurance_limited_sr=None, sickness_insurance_base=None, sickness_insurance_er=None, sickness_insurance_sr=None, syntec_base=None, syntec_er=None, syntec_sr=None, training_tax_base=None, training_tax_er=None, transport_payment_base=None, transport_payment_er=None, unemployment_insurance_slice_a_base=None, unemployment_insurance_slice_a_er=None, unemployment_insurance_slice_a_sr=None, unemployment_insurance_slice_b_base=None, unemployment_insurance_slice_b_er=None, unemployment_insurance_slice_b_sr=None, widowhood_insurance_base=None, widowhood_insurance_sr=None
##title=
##
True  = 1
False = 0

global paysheet
paysheet           = context.getObject()
paysheet_type      = paysheet.getPortalType()

paysheet_line_type = 'Pay Sheet Line'
paysheet_cell_type = 'Pay Sheet Cell'

employee            = paysheet.getDestinationSection()
employee_object     = paysheet.getDestinationSectionValue()
employer            = paysheet.getSourceSection()
employer_object     = paysheet.getSourceSectionValue()

gross_salary = abs(paysheet.getGrossSalary())
#paysheet_resource = paysheet.getCurrency()   why it doesn't work ?????
paysheet_resource = 'currency/EUR'



# set the title if empty
months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
if paysheet.getTitle() in ('', None):
    paysheet.setTitle('Salaire ' + str(employee_object.getTitle()) + ' ' + months[int(str(paysheet.getStartDate())[5:7])-1] + ' ' + str(paysheet.getStartDate())[0:4])



#########################################################################
# This part of the script implement functions to register all pay sheet
# informations from an ERP5 point of view.
#########################################################################

def createPaySheetItem(title='', res='', dest_org='', cells=[]):
    global paysheet
    # select good cells only
    good_cells = []
    for cell in cells:
        if cell["base"] not in ('', 0, None) and cell["rate"] not in ('', 0, None):
            good_cells.append(cell)
    if len(good_cells) == 0:
        return
    # get all variation categories used in cells
    var_cat_list = []
    for cell in good_cells:
        var_cat_list.append(cell["x"])
        var_cat_list.append(cell["y"])
    # add a new Pay Sheet Line
    payline = paysheet.newContent( portal_type                  = 'Pay Sheet Line'
                                 , title                        = title
                                 , resource                     = res
                                 , destination_section          = dest_org
                                 , destination                  = dest_org
                                 , variation_base_category_list = ('tax_category', 'salary_range')
                                 , variation_category_list      = var_cat_list
                                 )
    # fill each cell with values
    for cell in good_cells:
        paycell = payline.getCell(cell["x"], cell["y"], base_id = 'movement')
        paycell.edit(quantity=-cell["base"], price=cell["rate"]/100.0)



#########################################################################
# This part of script describe the behaviour of the calculation process
# from accountant point of view.
#########################################################################

# social organism
org_urssaf  = 'organisation/urssaf'
org_assedic = 'organisation/assedic'
org_arrco   = 'organisation/arrco'
org_agff    = 'organisation/agff'
org_agirc   = 'organisation/agirc'
org_apec    = 'organisation/apec'
org_etat    = 'organisation/etat'
org_ener    = 'organisation/henner'

# variation categories
cat_social_salary_share                     = 'tax_category/social/salary_share'
cat_social_employer_share                   = 'tax_category/social/employer_share'
cat_syntec_employer_share                   = 'tax_category/syntec_insurance/employer_share'
cat_syntec_salary_share                     = 'tax_category/syntec_insurance/salary_share'
cat_csg                                     = 'tax_category/csg/salary_share'
cat_crds                                    = 'tax_category/crds/salary_share'
cat_unemployment_salary_share               = 'tax_category/unemployment/salary_share'
cat_unemployment_employer_share             = 'tax_category/unemployment/employer_share'
cat_ags                                     = 'tax_category/ags/employer_share'
cat_supplementary_pension_salary_share      = 'tax_category/supplementary_pension/salary_share'
cat_supplementary_pension_employer_share    = 'tax_category/supplementary_pension/employer_share'
cat_life_insurance_employer_share           = 'tax_category/life_insurance/employer_share'
cat_apec_salary_share                       = 'tax_category/apec/salary_share'
cat_apec_employer_share                     = 'tax_category/apec/employer_share'
cat_taxes                                   = 'tax_category/taxes/employer_share'
cat_gross_salary                            = 'salary_range/france/salaire_brut'
cat_limited_salary                          = 'salary_range/france/salaire_plafonne'
cat_syntec_limited_salary                   = 'salary_range/france/salaire_plafonne_syntec'
cat_brut_csg_salary                         = 'salary_range/france/salaire_brut_csg'
cat_brut_crds_salary                        = 'salary_range/france/salaire_brut_crds'
cat_slice_a                                 = 'salary_range/france/tranche_a'
cat_slice_b                                 = 'salary_range/france/tranche_b'
cat_slice_c                                 = 'salary_range/france/tranche_c'
cat_slice_1                                 = 'salary_range/france/tranche_1'
cat_slice_2                                 = 'salary_range/france/tranche_2'


# sickness insurance = assurance maladie
createPaySheetItem( title       = 'Assurance maladie'
                  , res         = 'service/sickness_insurance'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_salary_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : sickness_insurance_base
                                        , "rate"    : sickness_insurance_sr
                                        },
                                        { "x"       : cat_social_employer_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : sickness_insurance_base
                                        , "rate"    : sickness_insurance_er
                                        }
                                    ]
                  )

# old-age insurance = assurance vieillesse
createPaySheetItem( title       = 'Assurance vieillesse'
                  , res         = 'service/oldage_insurance'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_salary_share
                                        , "y"       : cat_limited_salary
                                        , "base"    : oldage_insurance_limited_base
                                        , "rate"    : oldage_insurance_limited_sr
                                        },
                                        { "x"       : cat_social_employer_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : oldage_insurance_base
                                        , "rate"    : oldage_insurance_er
                                        },
                                        { "x"       : cat_social_employer_share
                                        , "y"       : cat_limited_salary
                                        , "base"    : oldage_insurance_limited_base
                                        , "rate"    : oldage_insurance_limited_er
                                        }
                                    ]
                  )

# widowhood insurance = assurance veuvage
createPaySheetItem( title       = 'Assurance veuvage'
                  , res         = 'service/widowhood_insurance'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_salary_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : widowhood_insurance_base
                                        , "rate"    : widowhood_insurance_sr
                                        }
                                    ]
                  )

# family benefits = allocations familiales
createPaySheetItem( title       = 'Allocations familiales'
                  , res         = 'service/family_benefits'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_employer_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : family_benefits_base
                                        , "rate"    : family_benefits_er
                                        }
                                    ]
                  )

# industrial accident = accidents du travail
createPaySheetItem( title       = 'Accidents du travail'
                  , res         = 'service/industrial_accident'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_employer_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : industrial_accident_base
                                        , "rate"    : industrial_accident_er
                                        }
                                    ]
                  )

# lodging helps = aide au logement
createPaySheetItem( title       = 'Aide au logement'
                  , res         = 'service/lodging_helps'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_employer_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : lodging_helps_base
                                        , "rate"    : lodging_helps_er
                                        },
                                        { "x"       : cat_social_employer_share
                                        , "y"       : cat_limited_salary
                                        , "base"    : lodging_helps_limited_base
                                        , "rate"    : lodging_helps_limited_er
                                        }
                                    ]
                  )

# transport payment = versement au transport
createPaySheetItem( title       = 'Versement au transport'
                  , res         = 'service/transport_payment'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_social_employer_share
                                        , "y"       : cat_gross_salary
                                        , "base"    : transport_payment_base
                                        , "rate"    : transport_payment_er
                                        }
                                    ]
                  )

# CSG = Contribution Sociale Generalisee (déductible / non déductible)
createPaySheetItem( title       = 'CSG deductible'
                  , res         = 'service/csg_deductible'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_csg
                                        , "y"       : cat_brut_csg_salary
                                        , "base"    : csg_deductible_base
                                        , "rate"    : csg_deductible_sr
                                        }
                                    ]
                  )
createPaySheetItem( title       = 'CSG non deductible'
                  , res         = 'service/csg_non_deductible'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_csg
                                        , "y"       : cat_brut_csg_salary
                                        , "base"    : csg_non_deductible_base
                                        , "rate"    : csg_non_deductible_sr
                                        }
                                    ]
                  )

# CRDS = Contribution pour le Remboursement de la Dette Sociale
createPaySheetItem( title       = 'CRDS imposable'
                  , res         = 'service/crds'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_crds
                                        , "y"       : cat_brut_crds_salary
                                        , "base"    : crds_base
                                        , "rate"    : crds_sr
                                        }
                                    ]
                  )

# unemployment insurance = assurance chomage
createPaySheetItem( title       = 'Assurance chomage'
                  , res         = 'service/unemployment_insurance'
                  , dest_org    = org_assedic
                  , cells       =   [   { "x"       : cat_unemployment_salary_share
                                        , "y"       : cat_slice_a
                                        , "base"    : unemployment_insurance_slice_a_base
                                        , "rate"    : unemployment_insurance_slice_a_sr
                                        },
                                        { "x"       : cat_unemployment_employer_share
                                        , "y"       : cat_slice_a
                                        , "base"    : unemployment_insurance_slice_a_base
                                        , "rate"    : unemployment_insurance_slice_a_er
                                        },
                                        { "x"       : cat_unemployment_salary_share
                                        , "y"       : cat_slice_b
                                        , "base"    : unemployment_insurance_slice_b_base
                                        , "rate"    : unemployment_insurance_slice_b_sr
                                        },
                                        { "x"       : cat_unemployment_employer_share
                                        , "y"       : cat_slice_b
                                        , "base"    : unemployment_insurance_slice_b_base
                                        , "rate"    : unemployment_insurance_slice_b_er
                                        }
                                    ]
                  )

# AGS (FNGS)
createPaySheetItem( title       = 'AGS'
                  , res         = 'service/ags'
                  , dest_org    = org_assedic
                  , cells       =   [   { "x"       : cat_ags
                                        , "y"       : cat_slice_a
                                        , "base"    : ags_slice_a_base
                                        , "rate"    : ags_slice_a_er
                                        },
                                        { "x"       : cat_ags
                                        , "y"       : cat_slice_b
                                        , "base"    : ags_slice_b_base
                                        , "rate"    : ags_slice_b_er
                                        }
                                    ]
                  )

# ARRCO
createPaySheetItem( title       = 'ARRCO'
                  , res         = 'service/arrco'
                  , dest_org    = org_arrco
                  , cells       =   [   { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_1
                                        , "base"    : arrco_slice_1_base
                                        , "rate"    : arrco_slice_1_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_1
                                        , "base"    : arrco_slice_1_base
                                        , "rate"    : arrco_slice_1_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_2
                                        , "base"    : arrco_slice_2_base
                                        , "rate"    : arrco_slice_2_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_2
                                        , "base"    : arrco_slice_2_base
                                        , "rate"    : arrco_slice_1_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_a
                                        , "base"    : arrco_slice_a_base
                                        , "rate"    : arrco_slice_a_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_a
                                        , "base"    : arrco_slice_a_base
                                        , "rate"    : arrco_slice_a_er
                                        }
                                    ]
                  )

# AGFF
createPaySheetItem( title       = 'AGFF'
                  , res         = 'service/agff'
                  , dest_org    = org_agff
                  , cells       =   [   { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_1
                                        , "base"    : agff_slice_1_base
                                        , "rate"    : agff_slice_1_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_1
                                        , "base"    : agff_slice_1_base
                                        , "rate"    : agff_slice_1_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_2
                                        , "base"    : agff_slice_2_base
                                        , "rate"    : agff_slice_2_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_2
                                        , "base"    : agff_slice_2_base
                                        , "rate"    : agff_slice_2_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_a
                                        , "base"    : agff_slice_a_base
                                        , "rate"    : agff_slice_a_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_a
                                        , "base"    : agff_slice_a_base
                                        , "rate"    : agff_slice_a_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_b
                                        , "base"    : agff_slice_b_base
                                        , "rate"    : agff_slice_b_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_b
                                        , "base"    : agff_slice_b_base
                                        , "rate"    : agff_slice_b_er
                                        }
                                    ]
                  )

# AGIRC
createPaySheetItem( title       = 'AGIRC'
                  , res         = 'service/agirc'
                  , dest_org    = org_agirc
                  , cells       =   [   { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_b
                                        , "base"    : agirc_slice_b_base
                                        , "rate"    : agirc_slice_b_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_b
                                        , "base"    : agirc_slice_b_base
                                        , "rate"    : agirc_slice_b_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_c
                                        , "base"    : agirc_slice_c_base
                                        , "rate"    : agirc_slice_c_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_c
                                        , "base"    : agirc_slice_c_base
                                        , "rate"    : agirc_slice_c_er
                                        }
                                    ]
                  )

# CET
createPaySheetItem( title       = 'CET'
                  , res         = 'service/cet'
                  , dest_org    = org_agirc
                  , cells       =   [   { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_a
                                        , "base"    : cet_slice_a_base
                                        , "rate"    : cet_slice_a_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_a
                                        , "base"    : cet_slice_a_base
                                        , "rate"    : cet_slice_a_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_b
                                        , "base"    : cet_slice_b_base
                                        , "rate"    : cet_slice_b_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_b
                                        , "base"    : cet_slice_b_base
                                        , "rate"    : cet_slice_b_er
                                        },
                                        { "x"       : cat_supplementary_pension_salary_share
                                        , "y"       : cat_slice_c
                                        , "base"    : cet_slice_c_base
                                        , "rate"    : cet_slice_c_sr
                                        },
                                        { "x"       : cat_supplementary_pension_employer_share
                                        , "y"       : cat_slice_c
                                        , "base"    : cet_slice_c_base
                                        , "rate"    : cet_slice_c_er
                                        }
                                    ]
                  )

# life insurance = assurance deces
createPaySheetItem( title       = 'Assurance deces'
                  , res         = 'service/life_insurance'
                  , dest_org    = org_urssaf
                  , cells       =   [   { "x"       : cat_life_insurance_employer_share
                                        , "y"       : cat_slice_a
                                        , "base"    : life_insurance_slice_a_base
                                        , "rate"    : life_insurance_slice_a_er
                                        }
                                    ]
                  )

# APEC
createPaySheetItem( title       = 'APEC'
                  , res         = 'service/apec'
                  , dest_org    = org_apec
                  , cells       =   [   { "x"       : cat_apec_salary_share
                                        , "y"       : cat_slice_b
                                        , "base"    : apec_slice_b_base
                                        , "rate"    : apec_slice_b_sr
                                        },
                                        { "x"       : cat_apec_employer_share
                                        , "y"       : cat_slice_b
                                        , "base"    : apec_slice_b_base
                                        , "rate"    : apec_slice_b_er
                                        }
                                    ]
                  )

# construction tax
createPaySheetItem( title       = 'Construction'
                  , res         = 'service/construction'
                  , dest_org    = org_etat
                  , cells       =   [   { "x"       : cat_taxes
                                        , "y"       : cat_gross_salary
                                        , "base"    : construction_tax_base
                                        , "rate"    : construction_tax_er
                                        }
                                    ]
                  )

# training tax
createPaySheetItem( title       = 'Apprentissage'
                  , res         = 'service/training_tax'
                  , dest_org    = org_etat
                  , cells       =   [   { "x"       : cat_taxes
                                        , "y"       : cat_gross_salary
                                        , "base"    : training_tax_base
                                        , "rate"    : training_tax_er
                                        }
                                    ]
                  )

# courses tax
createPaySheetItem( title       = 'Formation professionnelle'
                  , res         = 'service/courses_tax'
                  , dest_org    = org_etat
                  , cells       =   [   { "x"       : cat_taxes
                                        , "y"       : cat_gross_salary
                                        , "base"    : courses_tax_base
                                        , "rate"    : courses_tax_er
                                        }
                                    ]
                  )

# Syntec convention
createPaySheetItem( title       = 'Convention SYNTEC'
                  , res         = 'service/syntec_insurance'
                  , dest_org    = org_ener
                  , cells       =   [   { "x"       : cat_syntec_salary_share
                                        , "y"       : cat_syntec_limited_salary
                                        , "base"    : syntec_base
                                        , "rate"    : syntec_sr
                                        },
                                        { "x"       : cat_syntec_employer_share
                                        , "y"       : cat_syntec_limited_salary
                                        , "base"    : syntec_base
                                        , "rate"    : syntec_er
                                        }
                                    ]
                  )



#########################################################################
# Create all Pay sheet transaction lines
#########################################################################

#get_transaction().commit()
#context.PaySheetTransactionLine_generate()

# return to pay sheet
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=Pay+Sheet+Calculation+done.')
