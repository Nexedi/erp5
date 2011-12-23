<?php
  include('tiosafe_config.php');

  $order_id = "";
  if(postNotEmpty('sale_order_id'))
    $order_id = $_POST['sale_order_id'];

  //$store_name = getStoreName ($db);
  // créer une commande avec une taxe et un coupon pour avoir un bon test

  $req_select  = "SELECT DISTINCT ordr.orders_id AS id, ";
  #$req_select .= "CONCAT('Sale Order', ' ', ordr.orders_id) AS title, ";
  $req_select .= "ordr.customers_id AS person_id, ";
  $req_select .= "ordr.orders_id AS reference, ";
  $req_select .= "currency AS currency, ";
  
  $req_select .= "IF (ordr.billing_company is not NULL, ordr.billing_company, '') AS billing_company, ";
  /*$req_select .= "adr_billing.entry_firstname AS billing_firstname, ";
  $req_select .= "adr_billing.entry_lastname AS billing_lastname, ";*/
  $req_select .= "ordr.billing_name AS billing_firstname, ";
  $req_select .= "ordr.billing_country AS billing_country, ";
  $req_select .= "cst.customers_email_address AS email, ";
  //$req_select .= "ordr.user_email is not NULL, usr_info.user_email, '') AS user_email, ";
  
  $req_select .= "IF (ordr.delivery_company is not NULL, ordr.delivery_company, '') AS delivery_company, ";
  /*$req_select .= "adr_delivery.entry_firstname AS delivery_firstname, ";
  $req_select .= "adr_delivery.entry_lastname AS delivery_lastname, ";*/
  $req_select .= "ordr.delivery_name AS delivery_firstname, ";
  $req_select .= "ordr.delivery_country AS delivery_country, ";
  //$req_select .= "cst.customers_email_address AS email, ";
 
  $req_select .= "payment_method AS payment_method, ";
  $req_select .= "date_purchased AS start_date, ";
  $req_select .= "orders_date_finished AS stop_date ";
  $req_select .= "FROM ". TABLE_ORDERS ." ordr ";
  $req_select .= "LEFT OUTER JOIN ". TABLE_CUSTOMERS ." cst ON ordr.customers_id=cst.customers_id ";
  $req_select .= "LEFT OUTER JOIN ". TABLE_ADDRESS_BOOK ." adr_billing 
                       ON (ordr.customers_id=adr_billing.customers_id 
                           AND CONCAT(adr_billing.entry_firstname, ' ', adr_billing.entry_lastname)=billing_name
                           AND adr_billing.entry_street_address=billing_street_address) ";
  $req_select .= "LEFT OUTER JOIN ". TABLE_ADDRESS_BOOK ." adr_delivery 
                       ON (ordr.customers_id=adr_delivery.customers_id 
                           AND CONCAT(adr_delivery.entry_firstname, ' ', adr_delivery.entry_lastname)=delivery_name
                           AND adr_delivery.entry_street_address=delivery_street_address) ";
  //$req_select .= "LEFT OUTER JOIN ". orders_total ." tot ON (ordr.orders_id=tot.orders_id) ";
  //$req_select .= "LEFT OUTER JOIN ". TABLE_CUSTOMERS ." cst ON ordr.customers_id=cst.customers_id ";
  //$req_select .= "LEFT OUTER JOIN ". TABLE_ADDRESS_BOOK ." adr ON cst.customers_default_address_id=adr.address_book_id ";
  
  $req_select .= "WHERE ordr.orders_status  = '1' ";
  if($order_id != "") 
    $req_select .= "AND ordr.orders_id = '".$order_id."' ";
  $req_select .= "ORDER BY ordr.orders_id ASC";

  //Parcourir les commandes et fabriquer la réponse XML
  $result2 = $db->Execute($req_select);

   //print_r($result2);

   $xml = '<xml>';

    while (!$result2->EOF) {
      $xml .= '<object>';
      foreach ($result2->fields as $fieldname => $fieldvalue) {

         if(!empty($fieldvalue)) {

              if($fieldname=='id') {
              //Get Shipping details
              $req_select_1  = "SELECT ";
              $req_select_1 .= "tot.value AS delivery_price, ";
              $req_select_1 .= "shipping_method AS delivery_title, ";
              $req_select_1 .= "'0.00' AS delivery_tax_rate ";
              $req_select_1 .= "FROM ". TABLE_ORDERS ." ordr ";
              $req_select_1 .= "LEFT OUTER JOIN ". orders_total ." tot ON (ordr.orders_id=tot.orders_id 
                                AND tot.class='ot_shipping') ";
              $req_select_1 .= "WHERE ordr.orders_status  = '1'  AND tot.value>0 ";
              $req_select_1 .= "AND ordr.orders_id = '".$fieldvalue."' ";
              $result_select_1  = $db->Execute($req_select_1);
               
              if($result_select_1->RecordCount() > 0) {
                $xml1="";
                foreach ($result_select_1->fields as $fieldname1 => $fieldvalue1) {
                  if(!empty($fieldvalue1))
                  $xml1 .= '<'.$fieldname1.'>'. sanitizeStringForXML($fieldvalue1) .'</'.$fieldname1.'>';
                }
              }

              //Get discount details
              $req_select_2  = "SELECT ";
              $req_select_2 .= "tot.value AS discount_price, ";
              $req_select_2 .= "coupon_code AS discount_code, ";
              $req_select_2 .= "CONCAT('Discount ',coupon_code) AS discount_title, ";
              $req_select_2 .= "'0.00' AS discount_tax_rate ";
              $req_select_2 .= "FROM ". TABLE_ORDERS ." ordr ";
              $req_select_2 .= "LEFT OUTER JOIN ". orders_total ." tot ON (ordr.orders_id=tot.orders_id 
                                AND tot.class='ot_coupon') ";
              $req_select_2 .= "WHERE ordr.orders_status  = '1' AND tot.value>0 ";
              $req_select_2 .= "AND ordr.orders_id = '".$fieldvalue."' ";
              $result_select_2  = $db->Execute($req_select_2);

              if($result_select_2->RecordCount() > 0) {
                $xml2="";
                foreach ($result_select_2->fields as $fieldname2 => $fieldvalue2) {
                  if(!empty($fieldvalue2))
                  $xml2 .= '<'.$fieldname2.'>'. sanitizeStringForXML($fieldvalue2) .'</'.$fieldname2.'>';
                }
              }
           }
              
           $xml .= '<'.$fieldname.'>'. sanitizeStringForXML($fieldvalue) .'</'.$fieldname.'>';
             
        }
      }
      
      $xml .= $xml1;
      $xml .= $xml2;
      $xml .= '</object>';
      $result2->MoveNext();
    }
    $xml .= '</xml>'; 

  echo $xml;
  header('Content-type: text/xml');
  //echo executeSQL($req_select_1, $db);

  $db->close();

?> 
