<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."product_attribute (";
  $sql .= "id_product";
  $sql .= " ) VALUES ( ";
  $sql .= $_POST['id_product'];
  $sql .= ")";

  echo executeSQL($sql);
?>
