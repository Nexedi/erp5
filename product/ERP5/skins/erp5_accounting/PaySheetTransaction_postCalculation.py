## Script (Python) "PaySheetTransaction_postCalculation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=listbox=[], **kw
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



# delete all objects in the paysheet
id_list = []
for paysheet_item in paysheet.objectValues():
    id_list.append(paysheet_item.getId())
paysheet.manage_delObjects(id_list)



# this function register all paysheet informations in paysheet lines and cells
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



# set the title of the paysheet if empty
months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
if paysheet.getTitle() in ('', None):
    new_title = 'Salaire ' + str(employee_object.getTitle())
    if paysheet.getStartDate() not in ('', None):
        new_title = ' ' + months[int(str(paysheet.getStartDate())[5:7])-1] + ' ' + str(paysheet.getStartDate())[0:4]
    paysheet.setTitle(new_title)



# get the ordered list of standard preview line objects
std_lines = context.PaySheetTransaction_initializePreview()


# this list contain all paysheet items, indexed by service
paysheet_items = {}

# scan every standard preview line to create an item for each service
for std_line in std_lines:
    # get the service url (unique because containing the id)
    service = std_line.getProperty('service_url')
    # verify that the service is not existing
    if not paysheet_items.has_key(service):
        # create a temporary service item
        temp_item = {}
        # fill the new item with needed data
        temp_item['title']      = std_line.getProperty('title')
        temp_item['res']        = std_line.getProperty('service_url')
        temp_item['dest_org']   = std_line.getProperty('organisation_url')
        temp_item['cells']      = []
        # add the new service item to the list
        paysheet_items[service] = temp_item

# initialise the user preview line index
user_line_index = 0

# scan every standard preview line and get the correspondant user preview line to put user parameters in appropriate cells
for std_line in std_lines:
    # define some values related to current standard preview line
    service             = std_line.getProperty('service_url')
    salary_range_cat    = std_line.getProperty('salary_range_cat')
    tax_cat             = std_line.getProperty('tax_cat')
    # increment the user line index: we can use this strategy because preview lines (user or standard ones) are sorted
    user_line_index += 1
    # get user paysheet parameters stored in user preview line (=listbox)
    for user_line in listbox:
        # Base_viewSearchResultList the user preview line corresponding to the standard preview line
        if user_line.has_key('listbox_key') and int(user_line['listbox_key'])==user_line_index:
            # got it ! we have the right line
            # get the base salary
            base = user_line['base']
            # scan allowed tax categories to get employee and/or employer share rate
            for cat in tax_cat:
                # define an empty new cell
                new_cell = None
                mployee_r = user_line['employee_share_rate']
                mployer_r = user_line['employer_share_rate']
                if str(cat).find('employer_share') != -1 and mployer_r not in (None, ''):
                    new_cell =  { "x"       : cat
                                , "y"       : salary_range_cat
                                , "base"    : base
                                , "rate"    : mployer_r
                                }
                if str(cat).find('employee_share') != -1 and mployee_r not in (None, ''):
                    new_cell =  { "x"       : cat
                                , "y"       : salary_range_cat
                                , "base"    : base
                                , "rate"    : mployee_r
                                }
                # add the cell to the conresponding paysheet item
                if new_cell != None:
                    paysheet_items[service]['cells'].append(new_cell)

# create a paysheet item for each service with user data in it
for item in paysheet_items:
    if paysheet_items[item]['cells'] not in ([], None, ''):
        #print item
        createPaySheetItem  ( title     = paysheet_items[item]['title']
                            , res       = paysheet_items[item]['res']
                            , dest_org  = paysheet_items[item]['dest_org']
                            , cells     = paysheet_items[item]['cells']
                            )


# calculation of all paysheet transaction lines
#get_transaction().commit()
#context.PaySheetTransaction_generatePaySheetTransactionLineList()

context.immediateReindexObject()

# return to pay sheet
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=Pay+sheet+calculation+done.')
