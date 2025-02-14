sql_catalog = context.getPortalObject().portal_catalog.getSQLCatalog()

if value:
  subject_uid_list = [
    b.subject_set_uid for b in
    sql_catalog.SQLCatalog_zGetSubjectSetUid(subject_list=value)
  ]
  if subject_uid_list:
    return sql_catalog.buildQuery({
      "versioning.subject_set_uid": subject_uid_list,
    })

# query matching nothing
return sql_catalog.buildQuery({
  "uid": -1,
})
