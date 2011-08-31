<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 //Get the query string and complete the SQL query
  $user_id = "";
  if(isset($_POST['person_id'])) $user_id = $_POST['person_id'];
  
  
  // Generate the query
  $req_select  = "SELECT user_info_id AS id, ";
  $req_select .= "address_1 AS street, ";
  $req_select .= "zip AS zip, ";
  $req_select .= "city AS city, ";
  $req_select .= "country_name AS country ";
  $req_select .= "FROM ".constant('_VM_TABLE_PREFIX_')."_user_info usr ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_country ctr ";
  $req_select .= "ON usr.country=ctr.country_3_code ";

  $req_select .= "WHERE address_1 != 'no_street' AND zip != 'no_zip' 
                  AND country != 'no_country'  AND city != 'no_city' ";
  if($user_id!="")
    $req_select .= "AND  user_id = ".$user_id."  ";
  $req_select .= "ORDER BY user_info_id ASC";

  header('Content-type: text/xml');
  echo executeSQL($req_select);

  mysql_close();
 ?>