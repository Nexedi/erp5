<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  $sql = "UPDATE ".constant('_DB_PREFIX_')."product SET ";
  $sql .= "active=0 WHERE id_product=".$_POST['product_id'];

  echo executeSQL($sql);
?>
