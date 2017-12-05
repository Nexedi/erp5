from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
return ComplexQuery(
  SimpleQuery(grouping_reference=None),
  SimpleQuery(grouping_date=grouping_date, comparison_operator=">="),
  logical_operator="OR",
)
