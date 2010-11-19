<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the date
  $date = date('y-m-d H:i:s');

  # build the update of address
  $sql = "UPDATE ".constant('_DB_PREFIX_')."address SET ";
  # check which property must be updated
  $property_array = array(
    'street' => 'address1',
    'zip' => 'postcode',
    'city' => 'city',
  );
  foreach ($property_array as $property => $field) {
    if (isset($_POST[$property])) {
      if ($_POST[$property] != 'NULL') {
        $_POST[$property] = "'".$_POST[$property]."'";
      }
      $sql .= $field."=".$_POST[$property].", ";
    }
  }
  if (isset($_POST['country'])) {
    if ($_POST['country'] == 'NULL') {
      $sql .= 'id_country=0, ';
    } else {
      $sql .= "id_country=(SELECT id_country FROM ".constant('_DB_PREFIX_')."country_lang ";
      $sql .= "WHERE name='".$_POST['country']."' AND ";
      $sql .= "id_lang=".$_POST['language']."), ";
    }
  }
  $sql .= "date_upd='".$date."' ";
  # where clause which restrict to the good address
  $sql .= " WHERE id_address='".$_POST['address_id']."' AND id_customer='".$_POST['person_id']."'";

  echo executeSQL($sql);
?>
