Introduction
============

This recipe generates a new database on a mysql server.

Example
=======

You can use it with a part like this::

  [default-database]
  recipe = erp5.recipe.mysqldatabase
  mysql_database_name = somename
  mysql_user = root
  mysql_password = 
  mysql_superuser = root
  mysql_superpassword =
  

Options
=======

mysql_database_name
  Mysql Database name.

mysql_host
  Hostname which is running your mysql server. By Default uses localhost. 
  (Optional).
 
mysql_port
  Port Number which is running your mysql server. By Default uses 3306.
  (Optional).

mysql_user
  User of new database, used to grant privilegies on the new database.

mysql_password
  User's Password of new database, used to grant privilegies on the new 
  database.

mysql_superuser
  User of mysql used to connect to mysql server to create the database.
  
mysql_superpassword
  Password of user defined at mysql_superuser.

