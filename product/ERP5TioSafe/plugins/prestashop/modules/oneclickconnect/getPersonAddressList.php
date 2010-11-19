<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the sql which allows to retrieve the address of a person
  $sql = "SELECT ";
  $sql .= constant('_DB_PREFIX_')."address.id_address AS id, ";
  $sql .= constant('_DB_PREFIX_')."address.address1 AS street, ";
  $sql .= constant('_DB_PREFIX_')."address.postcode AS zip, ";
  $sql .= constant('_DB_PREFIX_')."address.city AS city, ";
  $sql .= constant('_DB_PREFIX_')."country_lang.name AS country ";

  # which tables are implied in the retrieve of address
  $sql .= "FROM ".constant('_DB_PREFIX_')."address " ;
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."country " ;
  $sql .= "ON ".constant('_DB_PREFIX_')."country.id_country=".constant('_DB_PREFIX_')."address.id_country ";
  $sql .= "LEFT JOIN ".constant('_DB_PREFIX_')."country_lang " ;
  $sql .= "ON ".constant('_DB_PREFIX_')."country_lang.id_country=".constant('_DB_PREFIX_')."country.id_country ";

  # where clause which restrict to the good person
  $sql .= "WHERE ";
  if (isset($_POST['person_id'])){
    $sql .= constant('_DB_PREFIX_')."address.id_customer=".$_POST['person_id']." AND ";
  }
  $sql .= constant('_DB_PREFIX_')."country_lang.id_lang=".$_POST['language']." AND ";
  $sql .= "address1 IS NOT NULL AND ";
  $sql .= "postcode IS NOT NULL AND ";
  $sql .= "city IS NOT NULL AND ";
  $sql .= constant('_DB_PREFIX_')."address.id_country IS NOT NULL AND ";
  $sql .= constant('_DB_PREFIX_')."address.active=1 AND ";
  $sql .= constant('_DB_PREFIX_')."address.deleted=0 ";

  # group the address by data
  $sql .= "GROUP BY address1, postcode, city, ".constant('_DB_PREFIX_')."address.id_country ";

  # FIXME: Is the order is usefull, the brain doesn't work on it ???
  # order by address id
  $sql .= "ORDER BY ".constant('_DB_PREFIX_')."address.id_address ASC ";

  echo executeSQL($sql);
?>
