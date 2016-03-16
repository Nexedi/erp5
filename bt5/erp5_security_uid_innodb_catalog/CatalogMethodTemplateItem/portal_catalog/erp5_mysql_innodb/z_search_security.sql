SELECT
  DISTINCT uid, local_roles_group_id
FROM 
  roles_and_users
WHERE 
  allowedRolesAndUsers 
  IN (<dtml-in security_roles_list><dtml-var sequence-item><dtml-if sequence-end><dtml-else>,</dtml-if></dtml-in>)
