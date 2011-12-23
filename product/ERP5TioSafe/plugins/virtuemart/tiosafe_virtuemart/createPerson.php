<?php exit(0);
  include("includes/config.inc.php");
  include("includes/function.php");

  //Define default values for address, if not set?
  $zip="no_zip";
  $city="no_city";
  $country="no_country";
  $street ="no_street";

  $title=$first_name=$last_name=$user_email="";

  /*$title="John Doe";
  $first_name="John";
  $last_name="Doe";
  $user_email="foo@foo.com";*/

  // Get posted parameters
  if(isset($_POST['title']))     $title = $_POST['title'];
  if(isset($_POST['firstname'])) $first_name = $_POST['firstname'];
  if(isset($_POST['lastname']))  $last_name = $_POST['lastname'];
  if(isset($_POST['email']))     $user_email = $_POST['email'];
  /*
  if(isset($_POST['street']))    $street = $_POST['street'];
  if(isset($_POST['zip']))       $zip = $_POST['zip'];
  if(isset($_POST['city']))      $city = $_POST['city'];
  if(isset($_POST['country']))   $country = $_POST['country']; */
 
  // Default Virtuemart users parameters
  $timestamp = time();
  $hash_secret = "VirtueMartIsCool";
  $user_info_id = md5(uniqid( $hash_secret));
  //$user_id =  $uid;
  $address_type =  'BT';
  $address_type_name =  '-default-';
  $cdate =  $timestamp; // creation date
  $mdate =  $timestamp; // modification date
  $name = $first_name; //
  $username=$first_name."_".$last_name;
  $username = strtolower(str_replace(" ", "_", trim($username)));
  $password = md5('AzertyuioP'); // Default password
  $usertype = 'Registered';
  $gid="18";


  //Firstname, Lastname and Email address are required
  if ($first_name!="" && $last_name!="" && $user_email!="" && $street!="" &&
      $zip!="" && $city!="" && $country!="") {
     
     if(!emailExists($user_email))
     {
       
       // create the users in default Jomla!1.5 users
       // XXX test if username doesn't exists before adding
       $personCreateQuery1 = sprintf("INSERT INTO ".constant('_JOOMLA_TABLE_PREFIX_')."users
                                      (name, username, email, password, usertype, gid) 
                                      Values (%s, %s, %s, %s, %s, %s)",
                                      GetSQLValueString($name, "text"), 
                                      GetSQLValueString($username, "text"), 
                                      GetSQLValueString($user_email, "text"), 
                                      GetSQLValueString($password, "text"), 
                                      GetSQLValueString($usertype, "text"),
                                      GetSQLValueString($gid, "int"));     
       //echo   $personCreateQuery1;
       $msg_1 = executeSQL($personCreateQuery1);
       // get the id of the inserted user
       $user_id = emailExists($user_email);
        
       // If we want the user to log in the virtuemart site
       $section_value = "users";
       $personCreateQuery1bis = sprintf("INSERT INTO ".constant('_JOOMLA_TABLE_PREFIX_')."core_acl_aro    
                                      ( section_value, value, name) 
                                      Values ( %s, %s, %s)",
                                      GetSQLValueString($section_value, "text"), 
                                      GetSQLValueString($user_id, "text"), 
                                      GetSQLValueString($name, "text"));       
       $msg_1bis = executeSQL($personCreateQuery1bis);

       
       // Create Virtuemart user
       $personCreateQuery2 = sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_user_info 
                                   (first_name, last_name, user_email, address_1, zip, city, country,
                                    address_type, address_type_name, cdate, mdate, user_id, user_info_id) 
                                    Values ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                    GetSQLValueString($first_name, "text"), 
                                    GetSQLValueString($last_name, "text"), 
                                    GetSQLValueString($user_email, "text"), 
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
       //echo $personCreateQuery2;
       $msg_2= executeSQL($personCreateQuery2);
       
       echo $msg_2;
      }
      else
         echo '\nVirtueMart Error: A user with the email \''.$user_email.'\' already exists!';
  }
  else 
    echo '\nInvalid query: firstname, lastname, email are required!';

  mysql_close();

 ?>