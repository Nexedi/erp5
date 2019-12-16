from json import dumps

connection = context
# make sure connection is open
connection()

tables = []
for table in connection.manage_test("SHOW TABLES"):
  columns = []
  for column in connection.manage_test("SHOW FULL COLUMNS FROM `%s`" % table[0]):
    columns.append({
      'columnName': column.field,
      'description': column.comment,
    })
  tables.append(
    {
      'tableName': table[0],
      'columns': columns
    }
  )

container.REQUEST.RESPONSE.setHeader('content-type', 'application/json')
return dumps(tables)
