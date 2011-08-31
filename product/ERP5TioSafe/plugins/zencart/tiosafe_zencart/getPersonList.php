<?php
  include('tiosafe_config.php');

  $customers_id = "";
  if(postNotEmpty ('person_id'))
    $customers_id = $_POST['person_id'];
    //$customers_id = 4;
  
  $req_select  = "SELECT cst.customers_id AS id, ";
  $req_select .= "CONCAT(customers_firstname, ' ', customers_lastname) AS title,   ";
  $req_select .= "customers_firstname AS firstname, ";
  $req_select .= "customers_lastname AS lastname, ";
  $req_select .= "customers_email_address AS email, ";
  //$req_select .= "IF (entry_company is NULL, '', adr.address_book_id)  AS company, ";
  $req_select .= "entry_company AS company, ";
  $req_select .= "customers_telephone  AS phone, ";
  $req_select .= "customers_dob AS birthday, ";
  
  $req_select .= "entry_street_address AS street, ";
  $req_select .= "entry_postcode  AS zip, ";
  $req_select .= "entry_city  AS city, ";
  $req_select .= "countries_name AS country, ";
  
  $req_select .= "'type/person' AS category ";
  $req_select .= "FROM ". TABLE_CUSTOMERS ." cst ";
  $req_select .= "LEFT JOIN ". TABLE_ADDRESS_BOOK ." adr ";
  $req_select .= "ON cst.customers_default_address_id = adr.address_book_id ";
  $req_select .= "LEFT JOIN ". TABLE_COUNTRIES ." cnt ";
  $req_select .= "ON adr.entry_country_id = cnt.countries_id ";
  
  $req_select .= " WHERE customers_firstname != '' AND customers_lastname != '' AND customers_email_address != ''";
  if(!empty($customers_id))
    $req_select .= "AND cst.customers_id='".$customers_id."' ";
  $req_select .= "ORDER BY firstname ASC, lastname ASC, email ASC";
 
  header('Content-type: text/xml');
  echo executeSQL($req_select, $db);
  
  $db->close();
?> 
