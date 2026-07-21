"""Return all modules which content must not be exposed to MCP server due to their sensitivity"""

return [
  "group_calendar_assignment_module",
  "time_table_module",
  "internal_supply_module",
  "extra_hour_module",
  "task_report_module",
  "allowed_old_task_module",
  "cxml_address_module",
  "organisational_unit_module",
]
