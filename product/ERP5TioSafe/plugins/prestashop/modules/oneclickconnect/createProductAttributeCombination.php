<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."product_attribute_combination VALUES ( ";

  # to put values in the database base, first, retrieve the attribute variation
  $sql .= "(";
  $sql .= "SELECT ".constant('_DB_PREFIX_')."attribute_lang.id_attribute ";
  $sql .= "FROM ".constant('_DB_PREFIX_')."attribute_lang ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."attribute ON ";
  $sql .= constant('_DB_PREFIX_')."attribute.id_attribute = ".constant('_DB_PREFIX_')."attribute_lang.id_attribute ";
  $sql .= " WHERE name='".$_POST['variation']."' AND id_attribute_group=";
  $sql .= "(SELECT id_attribute_group FROM ".constant('_DB_PREFIX_')."attribute_group_lang WHERE name='".$_POST['base_category']."')";
  $sql .= "), ";
  $sql .= $_POST['id_product_attribute'];
  $sql .= ")";

  echo executeSQL($sql);
?>
