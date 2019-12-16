"""Create deterministically transactions to test outputs of Reports."""
from DateTime import DateTime

portal = context.getPortalObject()
module = portal.accounting_module

# This option is necessary for RJS interface to render Reports
# If you'd keep XHTML value "View" the RJS will not crash it will
# only refuse to validate Report Form View
portal.AccountingZuite_setAccountReferencePreference(report_style=report_style)

# First, clean up the module
module.manage_delObjects(list(module.objectIds()))

# Create datasets
if report_name == "journal":
  module.AccountingModule_createAccountingTestReportJournalDataset()
elif report_name in ("trial-balance", "general-ledger"):
  module.AccountingModule_createAccountingTestReportDataset()
elif report_name in ("account-statement", "balance-sheet", "profit-and-loss"):
  module.AccountingModule_createAccountingTestReportDataset(two_banks=True)
elif report_name == "other-parties":
  module.AccountingZuite_createReportOtherPartiesDataset(with_ledger=False)
elif report_name == "other-parties-ledger":
  module.AccountingZuite_createReportOtherPartiesDataset()
elif report_name == "aged-balance":
  module.AccountingZuite_createReportAgedBalanceDataset()
else:
  raise RuntimeError('Unknown "{}" report - no create*Dataset defined'.format(
    report_name))

# test depends on this
return "Accounting Transactions Created."
