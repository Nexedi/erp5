# For backward compatibility, make sure to use python as default mode
mode = "python"
portal_type = context.getPortalType()
if portal_type == "Web Page":
  mode = "html"
elif portal_type == "Web Script":
  mode = "javascript"
elif portal_type == "Web Style":
  mode = "css"
return mode
