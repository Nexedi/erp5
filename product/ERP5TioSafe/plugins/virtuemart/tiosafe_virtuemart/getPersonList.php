<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 //Get the query string and complete the SQL query
  $organisation_id=$user_id ="";
  if(isset($_POST['person_id'])) $user_id = $_POST['person_id'];
  if(isset($_POST['organisation_id'])) $organisation_id = $_POST['organisation_id'];
  
  
  // Generate the query
  $req_select  = "SELECT user_id AS id, ";
  $req_select .= "CONCAT(first_name, ' ', last_name) AS title,   ";
  $req_select .= "first_name AS firstname, ";
  $req_select .= "last_name AS lastname, "; 
  $req_select .= "phone_1  AS phone, "; 
  $req_select .= "user_email AS email, ";
  //$req_select .= "IF (company is not NULL AND company !='', user_info_id,'' )  AS company, ";
  $req_select .= "IF (company is not NULL AND company !='', company,'' )  AS company, ";
  $req_select .= "IF (address_1='no_street', '', address_1)  AS street, ";
  $req_select .= "IF (zip='no_zip', '', zip)  AS zip, ";
  $req_select .= "IF (city='no_city', '', city) AS city, ";
  $req_select .= "IF (country_name='no_country', '', country_name)  AS country, ";
  //$req_select .= "'' as , ";

  $req_select .= "'type/Person' AS category ";
  $req_select .= "FROM ".constant('_JOOMLA_TABLE_PREFIX_')."users usr ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_user_info info ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_country ctr ";
  $req_select .= "ON info.country=ctr.country_3_code ";
  $req_select .= "ON usr.id=info.user_id AND address_type='BT'  ";
  $req_select .= "WHERE first_name != '' AND last_name != '' AND user_email != '' AND address_type='BT' ";
  
  if($user_id != "" )
    $req_select .= "AND user_id='".$user_id."' ";
  //if($organisation_id != "" )
    //$req_select .= "AND user_info_id='".$organisation_id."' ";

  $req_select .= "ORDER BY firstname ASC, lastname ASC, email ASC";

  header('Content-type: text/xml');
  echo executeSQL($req_select);

  mysql_close();
 ?>