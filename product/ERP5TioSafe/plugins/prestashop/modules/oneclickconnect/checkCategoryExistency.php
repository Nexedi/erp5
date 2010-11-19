<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the query which render the count of variations which correspond
  $sql = "SELECT ";
  $sql .= constant('_DB_PREFIX_')."attribute.id_attribute AS id, name AS title";

  # which tables are implied in the check of category existency
  $sql .= " FROM ".constant('_DB_PREFIX_')."attribute ";
  $sql .= " LEFT JOIN ".constant('_DB_PREFIX_')."attribute_lang ";
  $sql .= " ON ".constant('_DB_PREFIX_')."attribute_lang.id_attribute=".constant('_DB_PREFIX_')."attribute.id_attribute ";

  # check the good variation
  $sql .= "WHERE ";
  $sql .= "name='".$_POST['variation']."' AND ";
  $sql .= "id_lang=".$_POST['language']." AND ";
  $sql .= "id_attribute_group=(SELECT id_attribute_group FROM ".constant('_DB_PREFIX_')."attribute_group_lang WHERE name='".$_POST['base_category']."')";

  echo executeSQL($sql);
?>
