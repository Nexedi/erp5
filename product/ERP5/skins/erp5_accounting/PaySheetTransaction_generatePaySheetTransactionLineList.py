## Script (Python) "PaySheetTransaction_generatePaySheetTransactionLineList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
paysheet                        = context.getObject()
paysheet_type                   = paysheet.getPortalType()
paysheet_line_type              = 'Pay Sheet Line'
paysheet_transactionline_type   = 'Pay Sheet Transaction Line'
paysheet_cell_type              = 'Pay Sheet Cell'

employee            = paysheet.getDestinationSection()
employer            = paysheet.getSourceSection()
employer_object     = paysheet.getSourceSectionValue()


# gross salary source and destination
charge_salariale = 'account/charges_salariales'
produit_salarial = 'account/produits_salariaux'

# final salary source and destination
dette_salarie   = 'account/dettes_salaries'
creance_salarie = 'account/creances_salaries'

# employer share source and destination
charge_sociale = 'account/charges_sociales'
produit_social = 'account/produits_sociaux'

# employer + employee share source and destination
dette_sociale   = 'account/dettes_sociales'
creance_sociale = 'account/creances_sociales'

# the currency related to this french rules set is euros
paysheet_resource = 'currency/EUR'



# Create a new pay sheet line
def createPaySheetTransactionLine(new_title='', share='',
                                  src_sec='', src='', src_deb=None,
                                  dest_sec='', dest='', new_desc=''):
    suffix =    { 'social'  : ' (cotisations sociales)'
                , 'employer': ' (part patronale)'
                }
    if share == 'social' or share == 'employer':
        new_title += suffix[share]
        if share == 'social':
            src_sec  = employer
            src      = dette_sociale
            dest     = creance_sociale
        elif share == 'employer':
            src_sec  = employer
            src      = charge_sociale
            dest     = produit_social
    new_id = str(paysheet.generateNewId())
    context.portal_types.constructContent   ( type_name = paysheet_transactionline_type
                                            , container = paysheet
                                            , id        = new_id
                                            )
    # alternate method but doesn't work
    #new_line = paysheet.getObject(new_id)
    paysheet[new_id].setTitle(new_title)
    paysheet[new_id].setResource(paysheet_resource)
    paysheet[new_id].setSourceSection(src_sec)
    paysheet[new_id].setSource(src)
    paysheet[new_id].setDestinationSection(dest_sec)
    paysheet[new_id].setDestination(dest)
    paysheet[new_id].setSourceDebit(src_deb)
    paysheet[new_id].setDescription(new_desc)



def addAccountingItem(title='', mplyee_share=None, mplyer_share=None, dest_org=''):
    if mplyer_share == 0 and mplyee_share == 0:
        return
    if mplyer_share == 0:
        createPaySheetTransactionLine   ( new_title = title
                                        , share     = 'social'
                                        , src_deb   = mplyee_share
                                        , dest_sec  = dest_org
                                        )
        return
    if mplyee_share == 0:
        createPaySheetTransactionLine   ( new_title = title
                                        , share     = 'social'
                                        , src_deb   = mplyer_share
                                        , dest_sec  = dest_org
                                        )
        createPaySheetTransactionLine   ( new_title = title
                                        , share     = 'employer'
                                        , src_deb   = mplyer_share
                                        , dest_sec  = dest_org
                                        )
        return
    createPaySheetTransactionLine   ( new_title = title
                                    , share     = 'social'
                                    , src_deb   = float(mplyer_share) + float(mplyee_share)
                                    , dest_sec  = dest_org
                                    )
    createPaySheetTransactionLine   ( new_title = title
                                    , share     = 'employer'
                                    , src_deb   = mplyer_share
                                    , dest_sec  = dest_org
                                    )



# Only keep the PaySheetLine in the paysheet, delete all other objects
id_list = []
for paysheet_item in paysheet.objectValues():
    if paysheet_item.getPortalType() != paysheet_line_type:
        id_list.append(paysheet_item.getId())
paysheet.manage_delObjects(id_list)

# Get all amount
paysheet_details = paysheet.PaySheetTransaction_getDetails()
paysheet_categories = paysheet_details['paysheet_categories']

paysheet_formated_lines = []
for category in paysheet_categories:
  for line in paysheet_categories[category]['lines']:
    paysheet_formated_lines.append(line)

# Analyze every PaySheet Line
paysheet_lines = paysheet.objectValues()
for paysheet_item in paysheet_lines:
    if paysheet_item.getPortalType() == paysheet_line_type:

        # Find the dictionnary that contain the pre-calculated employer and employee share
        employer_share = 0.0
        employee_share = 0.0
        for line in paysheet_formated_lines:
            if line['id'] == paysheet_item.getId():
                er = line['employer_share']
                ee = line['employee_share']
                if er not in (None, ''):
                    employer_share += abs(float(er))
                if ee not in (None, ''):
                    employee_share += abs(float(ee))

        # Get the destination organisation
        paysheet_line_service = paysheet_item.getResourceValue()
        organisation = paysheet_line_service.getSource()

        # Add accounting item corresponding to the PaySheet Line
        addAccountingItem   ( title     = paysheet_item.getTitle()
                            , mplyer_share = employer_share
                            , mplyee_share = employee_share
                            , dest_org  = organisation
                            )

# Add the gross salary
createPaySheetTransactionLine   ( new_title = 'Salaire brut'
                                , src_sec   = employer
                                , src       = charge_salariale
                                , src_deb   = abs(float(paysheet_details['gross_salary']))
                                , dest_sec  = employee
                                , dest      = produit_salarial
                                )

# Add the final salary
createPaySheetTransactionLine   ( new_title = 'Salaire net'
                                , src_sec   = employer
                                , src       = dette_salarie
                                , src_deb   = abs(float(paysheet_details['net_salary']))
                                , dest_sec  = employee
                                , dest      = creance_salarie
                                )

# 'refresh' screen
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=Pay+Sheet+Transaction+Lines+created.')
