<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the sql which render the categories
  $sql = "SELECT ";
  $sql .= "DISTINCT(".constant('_DB_PREFIX_')."attribute_lang.name) AS distinction, ";
  $sql .= constant('_DB_PREFIX_')."product_attribute.id_product_attribute AS id, ";
  $sql .= "CONCAT(";
  $sql .= constant('_DB_PREFIX_')."attribute_group_lang.name, ";
  $sql .= " '/', ";
  $sql .= constant('_DB_PREFIX_')."attribute_lang.name ";
  $sql .= ") AS category ";

  # which tables are implied in the retrieve of product variations
  $sql .= "FROM ".constant('_DB_PREFIX_')."product ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."product_lang ";
  $sql .= "ON ".constant('_DB_PREFIX_')."product_lang.id_product=".constant('_DB_PREFIX_')."product.id_product ";

  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."product_attribute ";
  $sql .= "ON ".constant('_DB_PREFIX_')."product_attribute.id_product=".constant('_DB_PREFIX_')."product.id_product ";

  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."product_attribute_combination ";
  $sql .= "ON ".constant('_DB_PREFIX_')."product_attribute_combination.id_product_attribute=".constant('_DB_PREFIX_')."product_attribute.id_product_attribute ";

  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."attribute ";
  $sql .= "ON ".constant('_DB_PREFIX_')."attribute.id_attribute=".constant('_DB_PREFIX_')."product_attribute_combination.id_attribute ";

  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."attribute_lang ";
  $sql .= "ON ".constant('_DB_PREFIX_')."attribute_lang.id_attribute=".constant('_DB_PREFIX_')."attribute.id_attribute ";

  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."attribute_group_lang ";
  $sql .= "ON ".constant('_DB_PREFIX_')."attribute_group_lang.id_attribute_group=".constant('_DB_PREFIX_')."attribute.id_attribute_group ";

  # where clause which restrict to the good variations
  $sql .= "WHERE ";
  if (isset($_POST['product_id'])) {
    $sql .= constant('_DB_PREFIX_')."product.id_product=".$_POST['product_id']." AND ";
  } else if (isset($_POST['group_id'])) {
    $sql .= constant('_DB_PREFIX_')."product_attribute.id_product_attribute=".$_POST['group_id']." AND ";
  }
  $sql .= constant('_DB_PREFIX_')."product_lang.id_lang=".$_POST['language']." AND ";
  $sql .= constant('_DB_PREFIX_')."attribute_lang.id_lang=".$_POST['language']." AND ";
  $sql .= constant('_DB_PREFIX_')."attribute_group_lang.id_lang=".$_POST['language']." ";

  # group the render
  $sql .= "GROUP BY ";
  $sql .= constant('_DB_PREFIX_')."attribute_group_lang.name, ";
  $sql .= constant('_DB_PREFIX_')."attribute_lang.name ";

  # FIXME: Is the order is usefull, the brain doesn't work on it ???
  # order by group name and category name
  $sql .= "ORDER BY ";
  $sql .= constant('_DB_PREFIX_')."attribute_group_lang.name ASC, ";
  $sql .= constant('_DB_PREFIX_')."attribute_lang.name ASC ";

  echo executeSQL($sql);
?>
