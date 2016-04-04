""" 
This script will be called to apply the customization. 
"""

# Activate the knowledge pads on portal home to enable later the Wendelin 
# Information gadget.
#
configuration = self.portal.portal_preferences.getActivePreference()
configuration.setPreferredHtmlStyleAccessTab(True)
