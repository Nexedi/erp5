# Import Export

from Products.ERP5.Extensions.ImportExportSkins import importSkins
from Products.ERP5.Extensions.ImportExportSkins import exportSkins

fs_skin_ids = ('coramy_custom','coramy_trade', 'coramy_crm', 'coramy_manufacturing',
               'coramy_pdm','coramy_erp5','coramy_list_method','coramy_mrp')
fs_skin_dir = '/var/lib/zope/Products/Coramy/skins'
zodb_skin_ids = ('local_custom','local_trade', 'local_crm', 'local_manufacturing',
               'local_pdm','local_erp5','local_list_method','local_mrp')

def importCoramySkins(self, REQUEST=None):
  return importSkins(self, REQUEST=REQUEST, fs_skin_ids=fs_skin_ids, \
                zodb_skin_ids=zodb_skin_ids, \
                fs_skin_dir=fs_skin_dir)
def exportCoramySkins(self, REQUEST=None):
  return exportSkins(self, REQUEST=REQUEST, fs_skin_ids=fs_skin_ids, \
                zodb_skin_ids=zodb_skin_ids, \
                fs_skin_dir=fs_skin_dir)
