# -*- coding: utf-8 -*-

def accessSPL(result, browser):
  """
  This suite measure access time to a random sale packing list
  ERP5 site must contains a script Base_getRandomSPL with the
  following code :
  module = context.getPortalObject().sale_packing_list_module
  total = len(module)
  import random
  i = random.randint(0, total)
  spl = module.searchFolder(limit=(i,1))
  return spl.getId()
  """
  browser.mainForm.submitLogin()
  base_url = browser.url
  result('Get ID',
         browser.open(browser.url+'/Base_getRandomSPL'))
  spl_id = browser.contents
  url = base_url+'/sale_packing_list_module/%s/view'%(spl_id)
  result('Get SPL',
         browser.open(url))
  result('Reload SPL',
         browser.open(url))
  # Clear cookies so that haproxy distributes suite to another node
  browser.cookies.clearAll()
