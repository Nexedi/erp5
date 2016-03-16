"""
  This script should returns always two list of Business Template.
   - The first list is to resolve dependencies and upgrade.
   - The second list is what you want to keep. This is useful if we want to keep 
   a old business template without updating it and without removing it
"""

return ('erp5_base',), ["erp5_upgrader"]
