## Script (Python) "PaySheet_getReportLines"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
report_items = context.PaySheet_zGetDetailedTotal()

report_lines = []

# scan every sql report item
for item in report_items:
    line =  { 'title'               : None
            , 'employer_totalbase'  : None
            , 'employer_rate'       : None
            , 'employer_total'      : None
            , 'employee_totalbase'    : None
            , 'employee_rate'         : None
            , 'employee_total'        : None
            , 'total'               : None
            }
    # sort by employer/salary share
    if item['variation_text'].find('employee_share') != -1:
        line['title']               = item['parent_title']
        line['employee_totalbase']    = item['base']
        line['employee_rate']         = item['rate']
        line['employee_total']        = item['total_price']
    if item['variation_text'].find('employer_share') != -1:
        line['title']               = item['parent_title']
        line['employer_totalbase']  = item['base']
        line['employer_rate']       = item['rate']
        line['employer_total']      = item['total_price']
    report_lines.append(line)

# scan every line and group them

#here.portal

# first grouping:


return report_lines
