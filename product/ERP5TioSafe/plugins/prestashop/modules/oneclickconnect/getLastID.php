<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # through the type render the id of the corresponding data
  if ($_POST['type'] == 'Person') {
    $sql = "SELECT MAX(id_customer) AS last_id ";
    $sql .= "FROM ".constant('_DB_PREFIX_')."customer " ;
  } else if ($_POST['type'] == 'Product') {
    $sql = "SELECT MAX(id_product) AS last_id ";
    $sql .= "FROM ".constant('_DB_PREFIX_')."product " ;
  } else if ($_POST['type'] == 'Product Attribute') {
    $sql = "SELECT MAX(id_product_attribute) AS last_id ";
    $sql .= "FROM ".constant('_DB_PREFIX_')."product_attribute " ;
  }

  echo executeSQL($sql);
?>
