CREATE TABLE roles_and_users (
  uid INTEGER,
  allowedRolesAndUsers TEXT
);

CREATE INDEX roles_and_users_uid ON roles_and_users (uid);
CREATE INDEX roles_and_users_allowedRolesAndUsers ON roles_and_users (allowedRolesAndUsers);
