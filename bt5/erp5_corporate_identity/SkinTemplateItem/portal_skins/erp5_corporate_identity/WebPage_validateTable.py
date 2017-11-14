"""
================================================================================
Upgrade table for the specific type of display
================================================================================
"""
import re

# XXX set a meaningful caption
if table_string.find('caption=') == -1:
  return table.replace("</tbody>", '</tbody><caption>Table</caption')
