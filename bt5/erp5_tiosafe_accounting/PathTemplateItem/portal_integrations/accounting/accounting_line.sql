SELECT
  IF (journal_code in ('PI', 'PC'), '', CONCAT('Account ', account_code)) AS source_accounting,
  IF (journal_code in ('PI', 'PC'), CONCAT('Account ', account_code), '') AS destination_accounting,
  'Currency Euro' AS resource,
  IF (journal_code in ('PI', 'PC'), debit - credit, credit - debit) AS quantity,
  CONCAT('<dtml-var getPath>/accounting_module/', transaction_reference, ' ', journal_code, ' ', date) AS path,
  CONCAT('Accounting ', transaction_reference, ' ', journal_code, ' ', date) AS reference
FROM
  NOMACTX
<dtml-if expr="id_accounting or id_account">
WHERE
  <dtml-if expr="id_accounting">
    CONCAT(transaction_reference, ' ', journal_code, ' ', date) = <dtml-sqlvar type="string" expr="id_accounting">
  </dtml-if>
  <dtml-if expr="id_accounting and id_account">
    AND
  </dtml-if>
  <dtml-if expr="id_account">
    account_code = <dtml-sqlvar type="string" expr="id_account">
  </dtml-if>
</dtml-if>
ORDER BY
  transaction_reference ASC,
  journal_code ASC,
  date ASC
