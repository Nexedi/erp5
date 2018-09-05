"""
================================================================================
Get data to build a payslip report based on a person's paysheet transaction
================================================================================
"""
#
# parameters
# ------------------------------------------------------------------------------
# start_date                          start date of the report
# stop_date                           stop date of the report
#
# returns:
# {
#   "general_data_dict": {
#    "year": 2017,
#    "net_salary": "2 300.93",
#    "gross_salary": "3 085.28"
#  },
#  "cumulative_title_list": [
#    {"value": "Gross Salary", "is_header": True},
#    ...
#  ],
#  "cumulative_info_list":[
#    {"value": "3 085.28", "is_header": True},
#    ...
#  ],
#   'destination_address_line_list':  [
#      {"value": "USERTEST Slicea", "is_header": True},
#      {"value": "2 rue unerue"},
#      ...
#   ],
#   'destination_hiring_info_list': [
#      {"value": "Hiring Date: 1990/10/10"},
#      ...
#   ],
#   'destination_attendance_info_list': [
#     {"value": "Normal Working Hours": 151.67"},
#     ...
#   ]
#   'destination_vacation_info_list': [
#     {"value": "Earned this period: "},
#     ...
#   ],
#   'destination_taxation_info_list': [
#     {"value": "Price Currency: EUR"},
#   ],
#   'source_address_line_list: [
#      {"value": "Nexedi SA", "is_header": True},
#      {"value": "147 Rue du Ballon"}
#      ...
#   ],
#   source_corporate_info_line_list: [
#     {"value": "Corporate Registration Code: 440047504 00020"},
#     {"value": "Activity Code: 5829C"},
#     ...
#   ],
#   "payslip_section_list": [
#     [
#       {"value": "Usertest Slicea", "is_header": True, "value_base": "", "value_employee_share_rate": "", "value_employee_share": "", "value_employer_share_rate": "", "value_employer_share": ""},
#       {"value": "Salarie de Base", "value_base": "2 805.28", "value_employee_share_rate": "", "value_employee_share": "", "value_employer_share_rate": "", "value_employer_share": ""}
#     ], [
#        ...
#     ]
#  ]
#}

response = {
  "general_data_dict": {
    "year": "",
    "net_salary": "",
    "gross_salary": ""
  },
  "cumulative_title_list": [],
  "cumulative_info_list": [],
  "destination_address_line_list": [],
  "destination_hiring_info_list": [],
  "destination_attendance_info_list": [],
  "destination_vacation_info_list": [],
  "destination_taxation_info_list": [],
  "source_address_line_list": [],
  "source_corporate_info_line_list": [],
  "payslip_section_list": []
}
return response
