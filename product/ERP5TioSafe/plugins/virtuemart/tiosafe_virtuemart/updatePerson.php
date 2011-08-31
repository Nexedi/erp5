<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 
  // Default Virtuemart users values
  $timestamp = time();
  $hash_secret = "VirtueMartIsCool";
  $user_info_id = md5(uniqid( $hash_secret));
  //exit($user_info_id);
  //$user_id =  $uid;
  $address_type =  'BT';
  $address_type_name =  '-default-';
  $cdate =  $timestamp;
  $mdate =  $timestamp;
 
 
  $usr_id=$user_id=$title=$first_name=$last_name=$user_email="";
  if(isset($_POST['person_id'])) $user_id = $_POST['person_id'];
  if(isset($_POST['title']))     $title = $_POST['title'];
  if(isset($_POST['firstname'])) $first_name = $_POST['firstname'];
  if(isset($_POST['lastname']))  $last_name = $_POST['lastname'];
  if(isset($_POST['email']))     $user_email = $_POST['email'];
  if(isset($_POST['phone']))     $phone = $_POST['phone'];
 
  if(isset($_POST['street']))    $street = $_POST['street'];
  if(isset($_POST['zip']))        $zip = $_POST['zip'];
  if(isset($_POST['city']))       $city = $_POST['city'];
  if(isset($_POST['country']))    {
   $country_name = $_POST['country']; 
   $country = getCountryCode($country_name);
  }


  $name = $first_name;
  $username=$first_name."_".$last_name;
  $username = strtolower(str_replace(" ", "_", trim($username)));
  //$password = md5('AzertyuioP');
  //$usertype = 'Registered';

  //Firstname, Lastname and Email address are required
  if ($user_id!="" && ($first_name!="" || $last_name!="" || $user_email!="" || $phone !=""
                        || $street !=""  || $zip !=""  || $city !=""  || $country !="")) {
     if($user_email != "")
        $usr_id = emailExists($user_email);


     if(!$usr_id || $user_email=="" || ($usr_id==$user_id))
     {
       $separator="";
       // create the users in default Jomla!1.5 users
       $personUpdateQuery1  = "UPDATE ".constant('_JOOMLA_TABLE_PREFIX_')."users Set ";
       if($first_name!="") {
          $separator=',';
          $personUpdateQuery1 .= "name='".$name."' ";
       }
       if($first_name!="" and $last_name!="") {
          $personUpdateQuery1 .= $separator." username='".$username."' ";
          $separator=',';
       }
       if($user_email!="") {
          $personUpdateQuery1 .= $separator." email='".$user_email."' ";
       }
       $personUpdateQuery1 .= "WHERE id='".$user_id."' ";

      if($separator!="") {
         //echo $personUpdateQuery1;
         $msg_1 = executeSQL($personUpdateQuery1);
       }

       /*
       // If we want the user to log into the virtuemart site
       $table = constant('_JOOMLA_TABLE_PREFIX_')."core_acl_aro";
       $personUpdateQuery1bis = sprintf("UPDATE  ".$table."
                                         SET name=%s
                                         WHERE value=%s",
                                      GetSQLValueString($name, "text"), 
                                      GetSQLValueString($user_id, "text"));       
       //echo $personUpdateQuery1bis;
       $msg_1bis = executeSQL($personUpdateQuery1bis);
       */

       // Create Virtuemart user
       $separator="";
       // create the users in default Jomla!1.5 users
       $personUpdateQuery2  = "UPDATE ".constant('_VM_TABLE_PREFIX_')."_user_info SET ";
       if($first_name!="") {
          $personUpdateQuery2 .= " first_name='".$first_name."' ";
          $separator=',';
       }
       if($last_name!="") {
          $personUpdateQuery2 .= $separator." last_name='".$last_name."' ";
          $separator=',';
       }
       if($user_email!="") {
          $personUpdateQuery2 .= $separator." user_email='".$user_email."' ";
           $separator=',';
       } 
       if($phone!="") {
          $personUpdateQuery2 .= $separator." phone_1='".$phone."' ";
           $separator=',';
       } 
       if($street!="") {
          $personUpdateQuery2 .= $separator." address_1='".$street."' ";
           $separator=',';
       } 
       if($zip!="") {
          $personUpdateQuery2 .= $separator." zip='".$zip."' ";
           $separator=',';
       } 
       if($city!="") {
          $personUpdateQuery2 .= $separator." city='".$city."' ";
           $separator=',';
       } 
       if($country!="") {
          $personUpdateQuery2 .= $separator." country='".$country."' ";
           $separator=',';
       } 
       $personUpdateQuery2 .= $separator." mdate='".$mdate."' ";   
       $personUpdateQuery2 .= "WHERE user_id='".$user_id."' and address_type='".$address_type."'";

       $now = Date('dmY h:i:s');
       $fp = fopen("test.txt","a"); // ouverture du fichier en écriture
       fputs($fp, "\n---"); // on va a la ligne
       fputs($fp, $now." - ".$personUpdateQuery2.""); // on écrit le nom et email dans le fichier
       fclose($fp);

       if($separator!="") {
         //echo $personUpdateQuery2;
         $msg_2 = executeSQL($personUpdateQuery2);
         echo $msg_2;
       }
       else echo "<xml></xml>";
      }
      else
         echo '\nVirtueMart Error: A user with the email \''.$user_email.'\' already exists!';
  }
  else 
    echo '\nInvalid query: firstname, lastname, email, street, zip, city and country are required!';

  mysql_close();

 ?>