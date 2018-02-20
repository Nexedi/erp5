if process is None:
  return False
result_list = process.getResultList()
return bool(result_list and result_list[0].getProperty('severity'))
