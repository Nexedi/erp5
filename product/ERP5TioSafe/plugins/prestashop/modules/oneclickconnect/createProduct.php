<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the date
  $date = date('y-m-d H:i:s');

  # build the sql which create a product
  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."product ( ";
  $sql .= "ean13, reference, id_category_default, active, date_add, date_upd ";
  $sql .= " ) VALUES ( ";
  $sql .= (isset($_POST['ean13']) ? "'".$_POST['ean13']."'" : 'NULL').", ";
  $sql .= (isset($_POST['reference']) ? "'".$_POST['reference']."'" : 'NULL').", ";
  $sql .= "1, 1, '".$date."', '".$date."' ";
  $sql .= ") ";
  executeSQL($sql);

  # add the product name in the corresponding languages
  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."product_lang ( ";
  $sql .= "id_product, id_lang, link_rewrite, name ";
  $sql .= " ) VALUES ( ";
  $sql .= "(SELECT MAX(id_product) FROM ".constant('_DB_PREFIX_')."product), ";
  $sql .= $_POST['language'].', ';
  $sql .= "'".$_POST['title']."', '".$_POST['title']."' ";
  $sql .= ") ";
  executeSQL($sql);

  # add the product in the category
  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."category_product ( ";
  $sql .= "id_category, id_product, position ";
  $sql .= " ) VALUES ( ";
  $sql .= "1, ";
  $sql .= "(SELECT MAX(id_product) FROM ".constant('_DB_PREFIX_')."product), ";
  $sql .= "(SELECT MAX(id_product) FROM ".constant('_DB_PREFIX_')."product)";
  $sql .= ") ";

  echo executeSQL($sql);
?>
