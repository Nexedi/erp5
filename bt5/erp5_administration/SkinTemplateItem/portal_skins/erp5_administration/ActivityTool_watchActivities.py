print '<html><head><meta http-equiv="refresh" content="%s"></head><body>' % refresh_interval

for table in 'message', 'message_queue':
  q = """SELECT count(*) AS %(table)s, method_id, processing_node AS node, min(priority) AS min_pri, max(priority) AS max_pri
           FROM %(table)s GROUP BY method_id, processing_node ORDER BY node""" % dict(table=table)

  print "<table border=\"\" style=\"font-size:XX-small;\"><tbody> <tr><th>%s</th> <th>method_id</th> <th>node</th> <th>min_pri</th> <th>max_pri</th> </tr>" % table
  for row in context.cmf_activity_sql_connection.manage_test(q):
    print '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td</tr>' % (row[table], row['method_id'], row['node'], row['min_pri'], row['max_pri'])
  print '</tbody> </table> <br/>'

return printed
