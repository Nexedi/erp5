#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import subprocess


def git(*args):
  print("git", *args)
  print(subprocess.check_output(("git", ) + args, stderr=subprocess.STDOUT,).decode())


def rename(old, new):
  for root, dirs, files in os.walk(".", topdown=False):
    if ".git" in root.split(os.sep):
      continue
    for name in files:
      try:
        with open(os.path.join(root, name), 'r') as f:
          txt = f.read()
      except UnicodeDecodeError:
        #print("Error decoding", os.path.join(root, name), "skipping")
        continue
      if old in txt:
        with open(os.path.join(root, name), 'w') as f:
          f.write(txt.replace(old, new))
        git("add", os.path.join(root, name))
      name_without_extension, extension = os.path.splitext(name)
      if name_without_extension == old:
        git("mv", os.path.join(root, name), os.path.join(root, new) + extension)

    for name in dirs:
      if name == old:
        git("mv", os.path.join(root, name), os.path.join(root, new))

  git("commit", "-m", "Rename {} to {}".format(old, new))


for old, new in (
  ('PreferenceTool_resetAccountingTestDocumentSectionPreference', 'PreferenceTool_resetAccountingTestDocumentSectionPreference'),
  ('PreferenceTool_setAccountingTestDocumentSectionPreference', 'PreferenceTool_setAccountingTestDocumentSectionPreference'),
  ('PreferenceTool_setAccountingTestAccountReferencePreference', 'PreferenceTool_setAccountingTestAccountReferencePreference'),
  ('ERP5Site_resetConfigurationForAccountingTest', 'ERP5Site_resetConfigurationForAccountingTest'),
  ('Zuite_viewAccountingTestReportMacros', 'Zuite_viewAccountingTestReportMacros'),
  ('AccountingTransactionModule_markAccountingTestDataChanged', 'AccountingTransactionModule_markAccountingTestDataChanged'),
  ('AccountingTransactionModule_initializeAccountingTransactionTemplateTest', 'AccountingTransactionModule_initializeAccountingTransactionTemplateTest'),
  ('AccountingTransactionModule_initializeAccountingTransactionReportTest', 'AccountingTransactionModule_initializeAccountingTransactionReportTest'),
  ('ERP5Site_deleteAccountingTransactionTemplate', 'ERP5Site_deleteAccountingTransactionTemplate'),
  ('AccountingTransactionModule_createAccountingTestReportJournalDataset', 'AccountingTransactionModule_createAccountingTestReportJournalDataset'),
  ('AccountingTransactionModule_createAccountingTestReportDataset', 'AccountingTransactionModule_createAccountingTestReportDataset'),
  ('AccountingTransactionModule_createAccountingTestDocument', 'AccountingTransactionModule_createAccountingTestDocument'),
  ('AccountingTransactionModule_createAccountingTransactionListWithPersons', 'AccountingTransactionModule_createAccountingTransactionListWithPersons'),
  ('AccountingTransactionModule_createAccountingTransactionListSalesAndPayments', 'AccountingTransactionModule_createAccountingTransactionListSalesAndPayments'),
  # XXX make sure to replace in order, because this script is silly and it would replace AccountingTransactionModule_createAccountingTransactionList from AccountingTransactionModule_createAccountingTransactionListSalesAndPayments
  ('AccountingTransactionModule_createAccountingTransactionList', 'AccountingTransactionModule_createAccountingTransactionList'),
  ('ERP5Site_viewAccountingZuiteCommonTemplate', 'ERP5Site_viewAccountingZuiteCommonTemplate'),):
 rename(old, new)
