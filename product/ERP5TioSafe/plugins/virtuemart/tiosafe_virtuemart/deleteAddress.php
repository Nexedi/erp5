<?php
  include("includes/config.inc.php");
  include("includes/function.php");


  //Get the query string and complete the SQL query
  $user_id =$user_info_id= "";
  if(isset($_POST['person_id'])) $user_id = $_POST['person_id'];
  if(isset($_POST['address_id'])) $user_info_id = $_POST['address_id'];
  
  
  // Generate the query
  if($user_id !="" && $user_info_id !="") {

    //if default address, update with default empty no_address
    $default_address = isAddressDefault($user_info_id);

    if (!$default_address) {
      // Delete the customer's information
      $req_delete = "DELETE FROM ".constant('_VM_TABLE_PREFIX_')."_user_info WHERE user_id=".$user_id."";
      echo executeSQL($req_delete);
    }
    else { // Update the default address
      $address="no_adress";
      $zip="no_zip";
      $city="no_city";
      $country="no_country";
      $street ="no_street";

      $addressUpdateQuery1 = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_user_info SET
                                   ".$_PERS_PARAMS_MAPPING['address']."=%s, 
                                   ".$_PERS_PARAMS_MAPPING['zip']."=%s,
                                   ".$_PERS_PARAMS_MAPPING['city']."=%s, 
                                   ".$_PERS_PARAMS_MAPPING['country']."=%s
                                   WHERE user_info_id=%s ",
                                   GetSQLValueString($address, "text"), 
                                   GetSQLValueString($zip, "text"), 
                                   GetSQLValueString($city, "text"), 
                                   GetSQLValueString($country, "text"),
                                   GetSQLValueString($user_info_id, "int"));
       echo executeSQL($addressUpdateQuery1);
    }
  }
  else 
    echo '\nInvalid query: No parameter given!';
  mysql_close();

 ?>