<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 //Get the query string and complete the SQL query
  $person_id = "";
  if(isset($_POST['person_id'])) $person_id = $_POST['person_id'];
  
  // Generate the query
  $req_select  = "SELECT order_info_id  AS id, ";
  $req_select .= "first_name AS firstname, ";
  $req_select .= "last_name AS lastname, ";
  $req_select .= "user_email  AS email, "; 
  $req_select .= "phone_1  AS phone, "; 
  $req_select .= "IF (address_1='no_street', '', address_1)  AS street, ";
  $req_select .= "IF (zip='no_zip', '', zip)  AS zip, ";
  $req_select .= "IF (city='no_city', '', city) AS city, ";
  $req_select .= "IF (country_name='no_country', '', country_name)  AS country, ";
  //$req_select .= "IF (company is not NULL AND company!='' , order_info_id, '')  AS company, ";
  $req_select .= "IF (company is not NULL AND company!='' , company, '')  AS company, ";
  $req_select .= "'type/person' AS category ";
  $req_select .= "FROM ".constant('_VM_TABLE_PREFIX_')."_order_user_info usr ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_country ctr ";
  $req_select .= "ON usr.country=ctr.country_3_code ";
  $req_select .= "WHERE 1=1 ";
  if($person_id != "")
    $req_select .= "AND  order_info_id = '".$person_id."'  ";
  $req_select .= "ORDER BY order_info_id ASC";

  header('Content-type: text/xml');
  echo executeSQL($req_select);

  mysql_close();
 ?>