<?php
  include('tiosafe_config.php');

  
  $order_id = "";
  if(postNotEmpty('person_id'))
    $order_id = $_POST['person_id'];
  elseif(postNotEmpty('personnode_id'))
    $order_id = $_POST['personnode_id'];

  $req_select  = "SELECT ordr.orders_id AS id, ";
  $req_select .= "delivery_name AS title, ";
  $req_select .= "entry_firstname AS firstname, ";
  $req_select .= "entry_lastname AS lastname, ";
  $req_select .= "cst.customers_email_address AS email, ";
  $req_select .= "delivery_company AS company, ";
  $req_select .= "delivery_street_address AS street, ";
  $req_select .= "delivery_postcode  AS zip, ";
  $req_select .= "delivery_city AS city, ";
  $req_select .= "delivery_country  AS country, ";

  $req_select .= "'type/person' AS category ";
  $req_select .= "FROM ". TABLE_ORDERS ." ordr ";
  $req_select .= "RIGHT OUTER JOIN ". TABLE_CUSTOMERS ." cst ON ordr.customers_id=cst.customers_id ";
  $req_select .= "LEFT OUTER JOIN ". TABLE_ADDRESS_BOOK ." adr ON 
                      (ordr.customers_id=adr.customers_id 
                       AND CONCAT(adr.entry_firstname, ' ', adr.entry_lastname)=delivery_name
                       AND adr.entry_street_address=delivery_street_address) ";
  //cst.customers_default_address_id=adr.address_book_id 
  $req_select .= "LEFT OUTER JOIN ". TABLE_ORDERS_STATUS_HISTORY ." stat ON ordr.orders_id=stat.orders_id ";
  $req_select .= "WHERE orders_status_id  = '1' ";
  if($order_id != "") 
    $req_select .= "AND ordr.orders_id = '".$order_id."' ";
  $req_select .= "ORDER BY ordr.orders_id ASC";

  header('Content-type: text/xml');
  echo executeSQL($req_select, $db);

  $db->close();

?> 
