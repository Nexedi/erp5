## Script (Python) "PaySheetLinesPrintFormat"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
True  = 1
False = 0

pay_sheet = context.getObject()
all = pay_sheet.objectValues()

# this dictionnary contain all pay sheet details extracted from Pay Sheet Lines.
# these details are sorted and tidy for a clean print of the Pay Sheet
formated_lines = []             # id, title, pp, cs, ps
# todo: add: description assiette, montant assiette, pourcentage de la part salariale et patronale

# get all PaySheetLines
for pay_sheet_line in all:
    ID = pay_sheet_line.getId()
    if ID[-3:] == '_pp' or ID[-3:] == '_cs':
        # search an existing id without the suffix in the final table
        i = 0
        id_exist = False
        for line in formated_lines:
            if line['id'] == ID[:-3]:
                id_exist = True
                break
            i += 1
        # add a new line of contribution in pay sheet details
        if id_exist == False:
            new_formated_line = {   'id'        : ID[:-3],
                                    'title'     : None,
                                    'pp'        : None,
                                    'cs'        : None,
                                    'ps'        : None,
                                    'ps_desc'   : None,
                                    'pp_desc'   : None}
            formated_lines.append(new_formated_line)
        # get the employer share ('pp' is the french acronym of 'part patronale')
        if ID[-3:] == '_pp':
            formated_lines[i]['pp'] = pay_sheet_line.getDestinationCredit()
            formated_lines[i]['pp_desc'] = pay_sheet_line.getDescription()
        # get the social contribution (= employer + salary share) ('cs' is a french acronym of 'cotisation sociale')
        elif ID[-3:] == '_cs':
            formated_lines[i]['cs'] = pay_sheet_line.getDestinationCredit()
            formated_lines[i]['title'] = pay_sheet_line.getTitle()
            formated_lines[i]['ps_desc'] = pay_sheet_line.getDescription()

# calculation of the salary share ('ps' is a french acronym of 'part salariale')
for line in formated_lines:
    if line['cs']!=None and line['pp']!=None and line['cs']!=line['pp']:
        line['ps'] = float(line['cs']) - float(line['pp'])
    if line['cs']!=None and line['pp']==None:
        line['ps'] = float(line['cs'])


return formated_lines
