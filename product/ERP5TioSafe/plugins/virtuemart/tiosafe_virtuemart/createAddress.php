<?php
  include("includes/config.inc.php");
  include("includes/function.php");

   // Get posted parameters
  $user_id=$street=$zip=$city=$country="";
  
  /*$zip="99993";
  $city="City 3";
  $country="region/senegal";
  $country_path_array = explode("/", $country); $country_name= $country_path_array[1];
  $country = getCountryCode($country_name);
  $street ="Street 3";
  $user_id="86"; */
  
  //if(isset($_POST['id']))        $user_id = $_POST['id'];
  if(isset($_POST['person_id'])) $user_id = $_POST['person_id'];
  if(isset($_POST['street']))    $street = $_POST['street'];
  if(isset($_POST['zip']))       $zip = $_POST['zip'];
  if(isset($_POST['city']))      $city = $_POST['city'];
  if(isset($_POST['country']))   {
    $country_name = $_POST['country']; 
    $country = getCountryCode($country_name);
  }
 
  // Default Virtuemart users parameters
  $timestamp = time();
  $hash_secret = "VirtueMartIsCool";
  $user_info_id = md5(uniqid( $hash_secret));
  $address_type =  'ST';
  $address_type_name =  '-default-';
  $cdate =  $timestamp; // creation date
  $mdate =  $timestamp; // modification date


  if($user_id!="" && $street != "" && $zip!="" && $city!="" && $country!="") {
    //XXX How to idenify the default address
    //$default_address_set = isDefaultAddressSet($user_id);
   
    if(!isDefaultAddressSet($user_id)) { // Update the person's default address
      $address_type =  'BT';
      $addressUpdateQuery1 = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_user_info SET
                                   address_1=%s, 
                                   zip=%s,
                                   city=%s, 
                                   country=%s
                                   WHERE user_id=%s AND address_type=%s",
                                   GetSQLValueString($street, "text"), 
                                   GetSQLValueString($zip, "text"), 
                                   GetSQLValueString($city, "text"), 
                                   GetSQLValueString($country, "text"),
                                   GetSQLValueString($user_id, "int"),
                                   GetSQLValueString($address_type, "text"));
       //echo $addressUpdateQuery1;
       $msg_2 = executeSQL($addressUpdateQuery1);
       echo $msg_2;
    //user_id is required
    } else { // Create a new address
       
        // Create Virtuemart user
       $addressCreateQuery2 = sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_user_info 
                                   ( address_1, zip, city, country,
                                    address_type, address_type_name, cdate, mdate, user_id, user_info_id) 
                                    Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
//                                     GetSQLValueString($first_name, "text"), 
//                                     GetSQLValueString($last_name, "text"), 
                                    GetSQLValueString($street, "text"), 
                                    GetSQLValueString($zip, "text"), 
                                    GetSQLValueString($city, "text"), 
                                    GetSQLValueString($country, "text"),
                                    GetSQLValueString($address_type, "text"), 
                                    GetSQLValueString($address_type_name, "text"), 
                                    GetSQLValueString($cdate, "text"), 
                                    GetSQLValueString($mdate, "text"), 
                                    GetSQLValueString($user_id, "int"), 
                                    GetSQLValueString($user_info_id, "text"));
       echo $addressCreateQuery2;
       //$msg_1 = executeSQL($addressCreateQuery2);
       echo $msg_1;
     }

  }
  else 
    echo '\nInvalid query: address, zip, city and country are required!';

  mysql_close();

 ?>