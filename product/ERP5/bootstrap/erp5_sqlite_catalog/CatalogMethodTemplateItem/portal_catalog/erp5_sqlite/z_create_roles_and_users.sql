CREATE TABLE roles_and_users (
  uid INTEGER,
  allowedRolesAndUsers TEXT
);
<dtml-var sql_delimiter>
CREATE INDEX roles_and_users_uid ON roles_and_users (uid);
<dtml-var sql_delimiter>
CREATE INDEX roles_and_users_allowedRolesAndUsers ON roles_and_users (allowedRolesAndUsers);
