<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the sql which render the products or only one if the id is provided
  $sql = "SELECT ";
  $sql .= "DISTINCT(".constant('_DB_PREFIX_')."product.id_product) AS id_product, ";
  $sql .= constant('_DB_PREFIX_')."product.ean13 AS ean13, ";
  $sql .= constant('_DB_PREFIX_')."product.reference AS reference, ";
  $sql .= "(SELECT name FROM ".constant('_DB_PREFIX_')."product_lang WHERE id_product=".constant('_DB_PREFIX_')."product.id_product AND id_lang=".$_POST['language'].") AS title ";
  # which tables are implied in the render of products
  $sql .= "FROM ".constant('_DB_PREFIX_')."product " ;
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."product_lang " ;
  $sql .= "ON ".constant('_DB_PREFIX_')."product_lang.id_product=".constant('_DB_PREFIX_')."product.id_product ";
  $sql .= "WHERE ".constant('_DB_PREFIX_')."product.active=1 ";
  if (isset($_POST['product_id'])) {
    $sql .= "AND ".constant('_DB_PREFIX_')."product.id_product=".$_POST['product_id']." ";
  }

  # FIXME: Is the order is usefull, the brain doesn't work on it ???
  $sql .= "ORDER BY ";
  $sql .= constant('_DB_PREFIX_')."product_lang.name ASC, ";
  $sql .= constant('_DB_PREFIX_')."product.reference ASC ";

  echo executeSQL($sql);
?>
