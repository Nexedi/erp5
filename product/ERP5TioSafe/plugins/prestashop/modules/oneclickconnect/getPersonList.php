<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the sql which render the persons or only one if the id is provided
  $sql = "SELECT id_customer AS id, ";
  $sql .= "firstname AS firstname, lastname AS lastname, email AS email, ";
  $sql .= "DATE_FORMAT(birthday, '%Y/%m/%d') AS birthday ";
  $sql .= "FROM ".constant('_DB_PREFIX_')."customer " ;
  $sql .= "WHERE ";
  if (isset($_POST['person_id'])) {
    $sql .= "id_customer=".$_POST['person_id']." AND ";
  }
  $sql .= "firstname != '' AND lastname != '' AND email != '' AND deleted = 0 ";

  $sql .= "GROUP BY firstname, lastname, email ";
  # FIXME: Is the order is usefull, the brain doesn't work on it ???
  $sql .= "ORDER BY firstname ASC, lastname ASC, email ASC";

  echo executeSQL($sql);
?>
