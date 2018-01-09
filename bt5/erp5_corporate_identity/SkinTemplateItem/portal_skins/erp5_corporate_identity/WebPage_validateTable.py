"""
================================================================================
Upgrade table for the specific type of display
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# table_string                       "regexed" table string

# XXX set a meaningful caption
if table_string.find('caption=') == -1:
  return table_string.replace("</tbody>", '</tbody><caption>Table</caption')
