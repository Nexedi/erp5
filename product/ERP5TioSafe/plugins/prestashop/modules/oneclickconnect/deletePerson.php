<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # to remove someone, just put the deleted field to 1
  $sql = "UPDATE ".constant('_DB_PREFIX_')."customer SET ";
  $sql .= "deleted=1, active=0 ";
  $sql .= "WHERE id_customer=".$_POST['person_id'];

  echo executeSQL($sql);
?>
