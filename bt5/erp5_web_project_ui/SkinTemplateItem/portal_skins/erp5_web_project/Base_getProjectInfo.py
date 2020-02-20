import json
from datetime import datetime

def getProjectId(id):
  segments = id.split("/");
  if (len(segments) == 2):
    return id
  return "/".join(segments[0:-1])

project_dict = {}
now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#TODO these should be parameters
limit_date = "2019-12-19 00:00:00"
valid_states = ['planned', 'ordered', 'confirmed', 'delivered', 'ready']
valid_states = "('" + "', '".join(valid_states) + "')"
valid_types = ['Task', 'Bug', 'Task Report']
valid_types = "('" + "', '".join(valid_types) + "')"
# TODO: GET THE CATEGORY_UID
category = 282

query = """SELECT DISTINCT
            COUNT(*) AS  `#number`,
            `related_source_project__relative_url_1_catalog`.`relative_url` AS `source_project__relative_url`,
            `catalog`.`portal_type` AS `portal_type`
          FROM (catalog AS `catalog`
            LEFT JOIN ( category AS `related_source_project__relative_url_category`
            INNER JOIN catalog AS `related_source_project__relative_url_1_catalog`
            ON related_source_project__relative_url_category.base_category_uid = %i
              AND related_source_project__relative_url_1_catalog.uid = related_source_project__relative_url_category.category_uid)
            ON related_source_project__relative_url_category.uid = catalog.uid)
          WHERE
            1 = 1
            AND (`catalog`.`modification_date` <= "%s")
            AND `catalog`.`simulation_state` IN %s
            AND ( `catalog`.`portal_type` IN %s)
            AND ( `related_source_project__relative_url_1_catalog`.`relative_url` IS NOT NULL)
          GROUP BY
            `related_source_project__relative_url_1_catalog`.`relative_url`,
            `catalog`.`portal_type`"""

total_query = query % (category, now_date, valid_states, valid_types)

for row in context.cmf_activity_sql_connection.manage_test(total_query):
  key = getProjectId(row['source_project__relative_url'])
  if key in project_dict:
    project_dict[key][row['portal_type']] = { 'total' : row["#number"], 'outdated' : 0 }
  else:
    project_dict[key] = {row['portal_type'] : { 'total' : row["#number"], 'outdated' : 0 }}

outdated_query = query % (category, limit_date, valid_states, valid_types)

for row in context.cmf_activity_sql_connection.manage_test(outdated_query):
  key = getProjectId(row['source_project__relative_url'])
  project_dict[key][row['portal_type']]['outdated'] = row["#number"]

return json.dumps(project_dict, indent=2)
