for error_entry in context.error_log.getLogEntries():
  for key in error_entry:
    if key not in ["tb_text", "tb_html", 'req_html']:
      print('%s : %s' % (key, error_entry[key]))
  print('------------- Traceback ------------')
  print(error_entry["tb_text"])
  print("="*79)
return printed
