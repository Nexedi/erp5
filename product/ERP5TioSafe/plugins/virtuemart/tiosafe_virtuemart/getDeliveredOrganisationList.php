<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 //Get the query string and complete the SQL query
  $organisation_id=$title=$email="";
  if(isset($_POST['organisation_id'])) $organisation_id = $_POST['organisation_id'];
  if(isset($_POST['id'])) $organisation_id = $_POST['id'];
  if(isset($_POST['title'])) $title = $_POST['title'];
  if(isset($_POST['email']))  $email= $_POST['email'];
  
  // Generate the query
  $req_select  = "SELECT order_info_id  AS id, ";
  $req_select .= "company AS title, "; 
  $req_select .= "phone_1 AS phone, ";
  $req_select .= "fax AS fax, ";
  $req_select .= "user_email  AS email, "; 
  $req_select .= "IF (address_1='no_street', '', address_1)  AS street, ";
  $req_select .= "IF (zip='no_zip', '', zip)  AS zip, ";
  $req_select .= "IF (city='no_city', '', city) AS city, ";
  $req_select .= "IF (country_name='no_country', '', country_name)  AS country, ";
  $req_select .= "'type/organisation' AS category ";
  $req_select .= "FROM ".constant('_VM_TABLE_PREFIX_')."_order_user_info usr ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_country ctr ";
  $req_select .= "ON usr.country=ctr.country_3_code ";
  $req_select .= "WHERE company is not NULL AND company !='' ";
  if($organisation_id != "")
    $req_select .= "AND  order_info_id = '".$organisation_id."'  ";
  if($title != "")
    $req_select .= "AND  company = '".$title."'  ";
  if($email != "")
    $req_select .= "AND  user_email = '".$email."'  ";
  $req_select .= "ORDER BY order_info_id ASC";

  header('Content-type: text/xml');
  echo executeSQL($req_select);

  mysql_close();
 ?>