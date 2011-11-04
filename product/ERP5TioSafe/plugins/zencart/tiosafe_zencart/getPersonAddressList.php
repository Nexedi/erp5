<?php
  include('tiosafe_config.php');

  $customers_id = "";
  if(postNotEmpty ('person_id'))
    $customers_id = $_POST['person_id'];

  $req_select  = "SELECT address_book_id AS id, ";
  $req_select .= "entry_street_address AS street, ";
  $req_select .= "entry_postcode AS zip, ";
  $req_select .= "entry_city AS city, ";
  $req_select .= "cnt.countries_name AS country ";
  $req_select .= "FROM ". TABLE_ADDRESS_BOOK ." adr ";
  $req_select .= "LEFT OUTER JOIN ". TABLE_COUNTRIES ." cnt ";
  $req_select .= "ON adr.entry_country_id = cnt.countries_id ";
  if(!empty($customers_id))
    $req_select .= "WHERE adr.customers_id = ".$customers_id."  ";
  $req_select .= "ORDER BY address_book_id ASC";

  //header('Content-type: text/xml');
  //echo executeSQL($req_select, $db);

  $db->close();
?> 
