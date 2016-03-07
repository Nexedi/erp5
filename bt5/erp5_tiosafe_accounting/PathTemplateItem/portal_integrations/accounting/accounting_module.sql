SELECT
  DISTINCT(journal_code) AS type,
  transaction_reference AS reference,
  IF (journal_code in ('PI', 'PC'), CONCAT('Organisation ', third_party), 'Organisation MyFakeGidOrg') AS source_ownership,
  IF (journal_code in ('PI', 'PC'), 'Organisation MyFakeGidOrg', CONCAT('Organisation ', third_party)) AS destination_ownership,
  date AS start_date,
  date AS stop_date,
  CONCAT('Tax Code/', tax_code, '\nJournal/', journal_code) AS category,
  CONCAT('<dtml-var getPath>/accounting_module/', transaction_reference, ' ', journal_code, ' ', date) AS path,
  CONCAT('Accounting ', transaction_reference, ' ', journal_code, ' ', date) AS gid
FROM
  NOMACTX
<dtml-if id>
WHERE
  CONCAT(transaction_reference, ' ', journal_code, ' ', date) = <dtml-sqlvar type="string" expr="id">
</dtml-if>
GROUP BY
  transaction_reference,
  journal_code,
  date
ORDER BY
  transaction_reference ASC,
  journal_code ASC,
  date ASC
