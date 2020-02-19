import json
# TODO remove hardcoded fields and values, use script parameters
query = """SELECT DISTINCT COUNT(*) AS  `#number`  ,`related_source_project__relative_url_1_catalog`.`relative_url` AS `source_project__relative_url`,
                          `catalog`.`portal_type` AS `portal_type`, `catalog`.`modification_date` AS `modification_date`
            FROM (catalog AS `catalog`
              LEFT JOIN ( category AS `related_source_project__relative_url_category`
              INNER JOIN catalog AS `related_source_project__relative_url_1_catalog`
              ON related_source_project__relative_url_category.base_category_uid = 282 AND related_source_project__relative_url_1_catalog.uid = related_source_project__relative_url_category.category_uid)
              ON related_source_project__relative_url_category.uid = catalog.uid)
            WHERE
              1 = 1
              AND (`catalog`.`modification_date` >= "2019-02-19 10:02:00")
              AND `catalog`.`simulation_state` IN ('planned', 'ordered', 'confirmed', 'delivered', 'ready')
              AND ( `catalog`.`portal_type` IN ('Task', 'Bug', 'Task Report'))
              AND ( `related_source_project__relative_url_1_catalog`.`relative_url` IS NOT NULL)
            GROUP BY
              `related_source_project__relative_url_1_catalog`.`relative_url`, `catalog`.`portal_type`"""

project_dict = {'someproperty': 0, 'anotherproperty': 'value'}
project_dict = {}

def getProjectId(id):
  segments = id.split("/");
  if (len(segments) == 2):
    return id
  return "/".join(segments[0:-1])

for row in context.cmf_activity_sql_connection.manage_test(query):
  key = getProjectId(row['source_project__relative_url'])
  if key in project_dict:
    project_dict[key][row['portal_type']] = row["#number"]
  else:
    project_dict[key] = {row['portal_type'] : row["#number"]}

# TODO set number of outdated docs!!
# one query by "opened" state (total) and the same but filtering by modification date (outdated)

return json.dumps(project_dict, indent=2)
