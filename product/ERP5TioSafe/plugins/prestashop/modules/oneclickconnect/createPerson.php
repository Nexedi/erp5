<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the date
  $date = date('y-m-d H:i:s');

  # build the sql which create a person
  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."customer ( ";
  $sql .= "firstname, lastname, email, birthday, secure_key, passwd, active, deleted, date_add, date_upd";
  $sql .= " ) VALUES ( ";

  # set the values of the person and check if birthday is give
  $sql .= "'".$_POST['firstname']."', ";
  $sql .= "'".$_POST['lastname']."', ";
  $sql .= "'".$_POST['email']."', ";
  $sql .= (isset($_POST['birthday']) ? "'".$_POST['birthday']."'" : 'NULL').", ";
  $sql .= "'544ba9e0c36cc903cedcdcad8773f7ff', ";
  $sql .= "'4be012eb764d501233f79a33e1024042', ";
  $sql .= "1, 0, ";
  $sql .= "'".$date."', ";
  $sql .= "'".$date."' ) ";

  echo executeSQL($sql);
  # TODO: See to add a request and it's this request which "echo" the last id
?>
