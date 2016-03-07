from json import dumps
table_dict = {}

connection = context

# make sure connection is open
connection()

for table in connection.manage_test("SHOW TABLES"):
  table_dict[table[0]] = []
  for column in connection.manage_test("SHOW COLUMNS FROM `%s`" % table[0]):
    table_dict[table[0]].append(column[0])
    table_dict[table[0]].append("`%s`" % column[0])

container.REQUEST.RESPONSE.setHeader('content-type', 'application/json')
return dumps(table_dict)
