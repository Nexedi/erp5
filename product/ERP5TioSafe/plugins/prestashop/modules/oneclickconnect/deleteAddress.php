<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # to remove addresses of someone, put the deleted field to 1
  $sql = "UPDATE ".constant('_DB_PREFIX_')."address SET ";
  $sql .= "deleted=1, active=0 ";
  $sql .= "WHERE id_customer=".$_POST['person_id'];
  $sql .= (isset($_POST['address_id']) ? " AND id_address='".$_POST['address_id']."' " : '');

  echo executeSQL($sql);
?>
