<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # create the view which contains the element to remove
  $sql = "CREATE VIEW variation_combination_view AS ";
  $sql .= "SELECT DISTINCT(id_product_attribute) ";
  $sql .= "FROM ".constant('_DB_PREFIX_')."product_attribute_combination ";
  $sql .= "WHERE id_attribute=( ";
  $sql .= "  SELECT ".constant('_DB_PREFIX_')."attribute.id_attribute ";
  $sql .= "  FROM ".constant('_DB_PREFIX_')."attribute ";
  $sql .= "  LEFT JOIN ".constant('_DB_PREFIX_')."attribute_lang ";
  $sql .= "  ON ".constant('_DB_PREFIX_')."attribute_lang.id_attribute=".constant('_DB_PREFIX_')."attribute.id_attribute ";
  $sql .= "  WHERE name='".$_POST['variation']."' ";
  $sql .= "  AND id_lang=".$_POST['language'];
  $sql .= "  AND  id_attribute_group=( ";
  $sql .= "    SELECT id_attribute_group FROM ".constant('_DB_PREFIX_')."attribute_group_lang ";
  $sql .= "    WHERE name='".$_POST['base_category']."' AND id_lang=".$_POST['language'];
  $sql .= "  )";
  $sql .= " ) AND id_product_attribute IN ( ";
  $sql .= "  SELECT id_product_attribute ";
  $sql .= "  FROM ".constant('_DB_PREFIX_')."product_attribute ";
  $sql .= "  WHERE id_product=".$_POST['product_id'];
  $sql .= "); ";
  executeSQL($sql);

  # remove the element in the different tables
  $sql = "DELETE FROM ".constant('_DB_PREFIX_')."product_attribute_combination ";
  $sql .= "WHERE id_product_attribute IN (";
  $sql .= "  SELECT id_product_attribute FROM variation_combination_view";
  $sql .= ") ";
  executeSQL($sql);
  $sql = "DELETE FROM ".constant('_DB_PREFIX_')."product_attribute ";
  $sql .= "WHERE id_product_attribute IN (";
  $sql .= "  SELECT id_product_attribute FROM variation_combination_view";
  $sql .= ") ";
  executeSQL($sql);

  # remove the view
  $sql = "DROP VIEW variation_combination_view";

  echo executeSQL($sql);
?>
