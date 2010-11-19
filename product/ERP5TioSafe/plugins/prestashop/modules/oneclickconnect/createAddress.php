<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the date
  $date = date('y-m-d H:i:s');

  # build the sql which create a person
  $sql = "INSERT INTO ".constant('_DB_PREFIX_')."address ( ";
  $sql .= "id_country, id_customer, address1, postcode, city, active, deleted, date_add ";
  $sql .= " ) VALUES ( ";

  # first find the country in the tables and set the corresponding id
  if (isset($_POST['country'])) {
    $sql .= "(SELECT id_country FROM ".constant('_DB_PREFIX_')."country_lang ";
    $sql .= "WHERE name='".$_POST['country']."' AND id_lang=".$_POST['language']."), ";
  } else {
    $sql .= "'NULL', ";
  }

  # finnaly set the other element of the address
  $sql .= $_POST['person_id'].", ";
  $sql .= (isset($_POST['street']) ? "'".$_POST['street']."'" : 'NULL').", ";
  $sql .= (isset($_POST['zip']) ? "'".$_POST['zip']."'" : 'NULL').", ";
  $sql .= (isset($_POST['city']) ? "'".$_POST['city']."'" : 'NULL').", ";
  $sql .= "1, 0, '".$date."')";

  echo executeSQL($sql);
?>
