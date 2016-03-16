if process is None:
  return False
result_list = process.getResultList()
return result_list and bool(result_list[0].getProperty('severity')) or False
