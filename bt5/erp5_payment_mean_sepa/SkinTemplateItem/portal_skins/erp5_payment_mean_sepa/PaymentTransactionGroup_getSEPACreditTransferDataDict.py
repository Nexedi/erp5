section = context.getSourceSectionValue()
section_bank_account = context.getSourcePaymentValue()
assert section_bank_account.getValidationState() == 'validated'

currency = context.getPriceCurrencyReference() or context.getPriceCurrencyTitle()
assert currency.upper() == 'EUR', 'Wrong currency %s' % currency


data_dict = {
  'GrpHdr': {
    'MsgId': context.getSourceReference(),
    'CreDtTm': context.getStopDate().toZone('UTC').asdatetime().isoformat(),
    'InitgPty': {
      'Nm': section.getCorporateName() or section.getTitle(),
    }
  },
  'PmtInf': {
    'PmtInfId': context.getReference() or context.getSourceReference(),
    'ReqdExctnDt':context.getStopDate().toZone('UTC').asdatetime().strftime('%Y-%m-%d'),
    'Dbtr': {
      'Nm':  section.getCorporateName() or section.getTitle(),
    },
    'DbtrAcct': {
      'Id': {
        'IBAN': section_bank_account.getIban().replace(' ', '').replace('\t', ''),
      }
    },
    'DbtrAgt': {
      'FinInstnId': {
        'BIC': section_bank_account.getBicCode().strip(),
      }
    }
  },
}


# This does not support payment transactions with multiple lines.
# To prevent generating a file where the same end to end id exists twice,
# we just check that EndToEndId are unique in this file.
end_to_end_id_set = set([])

transaction_list = []
total = 0
for brain in context.PaymentTransactionGroup_getAccountingTransactionLineList():
  amount = round(-brain.total_quantity, 2)
  assert amount > 0
  total += amount

  transaction_line = brain.getObject()
  transaction = transaction_line.getExplanationValue()

  if brain.payment_uid == transaction_line.getSourcePaymentUid():
    creditor_entity = transaction_line.getDestinationSectionValue()
    creditor_bank_account = transaction_line.getDestinationPaymentValue()
  else:
    assert brain.payment_uid == transaction_line.getDestinationPaymentUid()
    creditor_entity = transaction_line.getSourceSectionValue()
    creditor_bank_account = transaction_line.getSourcePaymentValue()
  assert creditor_bank_account.getValidationState() == 'validated', \
    '%s is not validated' % creditor_bank_account.getRelativeUrl()

  assert transaction_line.AccountingTransactionLine_checkPaymentBelongToSection(source=True), \
    'source bank account on %s does not belong to section' % transaction_line.getRelativeUrl()
  assert transaction_line.AccountingTransactionLine_checkPaymentBelongToSection(source=False), \
    'destination bank account on %s does not belong to section' % transaction_line.getRelativeUrl()

  end_to_end_id = transaction.getReference()
  assert end_to_end_id
  assert end_to_end_id not in end_to_end_id_set
  end_to_end_id_set.add(end_to_end_id)

  transaction_list.append(
    {
      'PmtId': {
        'EndToEndId': end_to_end_id,
      },
      'RmtInf': {
        'Ustrd': transaction_line.AccountingTransactionLine_getSEPACreditTransferRemittanceInformation(),
      },
      'Cdtr': {
        'Nm': creditor_entity.getCorporateName() or creditor_entity.getTitle(),
        'PstlAdr': (creditor_entity.getDefaultAddressText() or '').splitlines(),
        'Ctry': creditor_entity.getDefaultAddressRegion() and creditor_entity.getDefaultAddressValue().getRegionReference(),
      },
      'Amt': {
        'InstdAmt': '%0.2f' % amount
      },
      'CdtrAcct': {
         'Id': {
           'IBAN': creditor_bank_account.getIban().replace(' ', '').replace('\t', ''),
         }
      },
      'CdtrAgt': {
        'FinInstnId': {
          'BIC': section_bank_account.getBicCode().strip(),
        }
      }
    }
  )

data_dict['GrpHdr']['NbOfTxs'] = len(transaction_list)
data_dict['GrpHdr']['CtrlSum'] = '%0.2f' % total
data_dict['transaction_list'] = transaction_list
return data_dict
