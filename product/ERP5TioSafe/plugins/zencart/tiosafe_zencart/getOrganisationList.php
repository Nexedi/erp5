<?php
  include('tiosafe_config.php');

  $organisation_id=$title=$email="";
  if(postNotEmpty('organisation_id')) 
    $organisation_id = $_POST['organisation_id'];
  if(postNotEmpty('title')) 
    $title = $_POST['title'];
  if(postNotEmpty('email')) 
    $email = $_POST['email'];
  
  
  $req_select  = "SELECT address_book_id AS id, ";
  $req_select .= "entry_company AS title,   ";
  //$req_select .= "entry_firstname AS firstname, ";
  //$req_select .= "entry_lastname AS lastname, ";
  $req_select .= "entry_street_address AS street, ";
  $req_select .= "entry_postcode  AS zip, ";
  $req_select .= "entry_city AS city, ";
  $req_select .= "countries_name  AS country, ";
  $req_select .= "customers_email_address AS email, ";
  $req_select .= "'type/organisation' AS category ";
  $req_select .= "FROM ". TABLE_ADDRESS_BOOK ." adr ";
  $req_select .= "LEFT JOIN ". TABLE_COUNTRIES ." cnt ";
  $req_select .= "ON adr.entry_country_id = cnt.countries_id ";
  $req_select .= "LEFT JOIN ". TABLE_CUSTOMERS ." cst ";
  $req_select .= "ON (adr.address_book_id = cst.customers_default_address_id OR 
                      adr.customers_id=cst.customers_id ) ";
  
  $req_select .= "WHERE entry_company is not NULL and entry_company != '' ";
  if(!empty($organisation_id))
    $req_select .= "AND address_book_id='".$organisation_id."' ";
  if($title != "")
    $req_select .= "AND  entry_company = '".$title."'  ";
  if($email != "")
    $req_select .= "AND  customers_email_address = '".$email."'  ";

  $req_select .= "ORDER BY entry_company ASC";
 
  header('Content-type: text/xml');
  echo executeSQL($req_select, $db);
  
  $db->close();
?> 
