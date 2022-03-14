last_message = context.getLastLog()[-1]
line_list = [_f for _f in last_message.replace("=\n","").split("\n") if _f]
for line in line_list:
  if "http" in line:
    return context.REQUEST.RESPONSE.redirect(line.replace("=3D", "="))

raise RuntimeError("URL not found in the email")
