<?php
  $path = explode('/modules',dirname(__FILE__));
  $config = $path[0].'/config/settings.inc.php';
  include($config);
  include('database.php');
  header('Content-Type: text/plain; charset=utf-8');

  # build the date
  $date = date('y-m-d H:i:s');

  # build the update of person
  $sql = "UPDATE ".constant('_DB_PREFIX_')."customer SET ";
  # check which property must be updated
  $property_array = array(
    'firstname' => 'firstname',
    'lastname' => 'lastname',
    'email' => 'email',
    'birthday' => 'birthday',
  );
  foreach ($property_array as $property => $field) {
    if (isset($_POST[$property])) {
      if ($_POST[$property] != 'NULL') {
        $_POST[$property] = "'".$_POST[$property]."'";
      }
      $sql .= $field."=".$_POST[$property].", ";
    }
  }
  $sql .= "date_upd='".$date."' WHERE id_customer=".$_POST['person_id'];

  echo executeSQL($sql);
?>
