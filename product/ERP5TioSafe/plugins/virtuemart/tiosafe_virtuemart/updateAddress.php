<?php
  include("includes/config.inc.php");
  include("includes/function.php");
 
 $user_info_id=$user_id=$address=$zip=$city=$country="";
 

  if(isset($_POST['address_id'])) $user_info_id = $_POST['address_id'];
  if(isset($_POST['person_id']))  $user_id = $_POST['person_id'];
  if(isset($_POST['street']))     $street = $_POST['street'];
  if(isset($_POST['zip']))        $zip = $_POST['zip'];
  if(isset($_POST['city']))       $city = $_POST['city'];
  if(isset($_POST['country']))    {
   $country_name = $_POST['country']; 
   $country = getCountryCode($country_name);
  }
  
  $now = Date('dmY h:i:s');
  $fp = fopen("test.txt","a"); // ouverture du fichier en écriture
  fputs($fp, "\n---"); // on va a la ligne
  fputs($fp, $now." - ".$user_info_id.""); // on écrit le nom et email dans le fichier
  fclose($fp);

  //user_info_id, address, zip, city and country are required!
  if ($user_info_id!="" and ($street!="" or $zip!="" or $city!="" or $country!="")) {
       
       $addressUpdateQuery1 = "UPDATE ".constant('_VM_TABLE_PREFIX_')."_user_info SET "; 
       $separator="";
       if($street != "") {
          $addressUpdateQuery1.="address_1=".GetSQLValueString($street, "text");
          $separator=",";
       }
       if($zip != "") {
          $addressUpdateQuery1.=$separator." zip=".GetSQLValueString($zip, "text");
          
          $separator=",";
       }
       if($city != "") {
          $addressUpdateQuery1.=$separator." city=".GetSQLValueString($city, "text");
          $separator=",";
       }
       if($country != "") {
          $addressUpdateQuery1.=$separator." country=".GetSQLValueString($country, "text");
       }

       if($separator!="") {
         $addressUpdateQuery1.=" WHERE user_info_id=".$user_info_id;
       }
       
       // Create Virtuemart user
       /*$addressUpdateQuery1 = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_user_info SET
                                   ".$sql_fields."
                                   WHERE user_info_id=%s ",
                                   $sql_fields_value
                                   GetSQLValueString($user_info_id, "int"));*/
       
       //echo $addressUpdateQuery1;
       
       $msg_2 = executeSQL($addressUpdateQuery1);
       echo $msg_2;
       
 
  }
  else 
    echo '\nInvalid query:  address, zip, city and country or required!';

  mysql_close();

 ?>