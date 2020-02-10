from Products.DCWorkflow.DCWorkflow import ValidationFailed

insolvency_proceeding = state_change['object']
if not insolvency_proceeding.hasReference():
  raise ValidationFailed(insolvency_proceeding.Base_translateString('Cannot open a insolvency proceeding without reference'))
if not insolvency_proceeding.hasContinuationOfActivity():
  raise ValidationFailed(insolvency_proceeding.Base_translateString('Cannot open a insolvency proceeding without continuation of activity defined'))
if not insolvency_proceeding.hasDestinationSection():
  raise ValidationFailed(insolvency_proceeding.Base_translateString('Cannot open a insolvency proceeding without debtor'))
if not insolvency_proceeding.hasSourceSection():
  raise ValidationFailed(insolvency_proceeding.Base_translateString('Cannot open a insolvency proceeding without creditor'))
