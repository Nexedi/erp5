<?php
  include('tiosafe_config.php');

  $order_id = "";
  if(postNotEmpty('sale_order_id'))
    $order_id = $_POST['sale_order_id'];

  $req_select  = "SELECT ordr.orders_id AS id, ";
  $req_select .= "delivery_company AS title, ";
  $req_select .= "delivery_street_address AS street, ";
  $req_select .= "delivery_postcode  AS zip, ";
  $req_select .= "delivery_city  AS city, ";
  $req_select .= "delivery_country AS country, ";
  $req_select .= "customers_telephone AS phone, ";
  $req_select .= "customers_email_address AS email, ";
  $req_select .= "'type/organisation' AS category ";
  $req_select .= "FROM ". TABLE_ORDERS ." ordr ";
  $req_select .= "LEFT JOIN ". TABLE_ORDERS_STATUS_HISTORY ." stat ON ordr.orders_id=stat.orders_id ";
  $req_select .= "WHERE orders_status_id  = '1' AND delivery_company is not NULL and delivery_company != ''";
  //AND (customers_company != billing_company AND customers_street_address != billing_street_address )
  if($order_id != "") 
    $req_select .= "AND ordr.orders_id = '".$order_id."' ";
  $req_select .= "ORDER BY ordr.orders_id ASC";

  header('Content-type: text/xml');
  echo executeSQL($req_select, $db);

  $db->close();

?> 
