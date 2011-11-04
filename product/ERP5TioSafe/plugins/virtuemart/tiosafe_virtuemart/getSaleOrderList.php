<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  

 //Get the query string and complete the SQL query
  $order_id = "";
  if(isset($_POST['sale_order_id']))
    $order_id = $_POST['sale_order_id'];

  
  // Generate the query
  $req_select  = "SELECT ordr.order_id AS id, ";
  $req_select .= "CONCAT('Sale Order ', ordr.order_id)  AS title, ";
  $req_select .= "usr.id AS person_id, ";
  $req_select .= "order_number AS reference, ";
  $req_select .= "order_currency AS currency, ";
  //$req_select .= "order_tax AS vat, ";
  //$req_select .= "'19.60' AS vat, ";
  
  $req_select .= "IF (order_shipping>0 , order_shipping, '0.00') AS delivery_price, ";
  $req_select .= "ship_method_id AS delivery_title, ";
  //$req_select .= "order_shipping_tax AS delivery_tax_rate, ";
  $req_select .= "IF (order_shipping_tax>0 , (order_shipping_tax/order_shipping), '0.00') AS delivery_tax_rate, ";
  
  $req_select .= "IF (coupon_discount>0, coupon_discount, '0') AS discount_price, ";
  $req_select .= "IF (coupon_code is not NULL, coupon_code, '') AS discount_code, ";
  $req_select .= "IF (coupon_discount>0 , CONCAT('Discount ',coupon_code), 'No Discount') AS discount_title, ";
  $req_select .= "'0.00' AS discount_tax_rate, ";
 

  
  /*# Source and Destination
  $req_select .= "'default_node' AS source, ";
  $req_select .= "CONCAT('', IFNULL(";
  $req_select .= "CONCAT(usr_info.user_id), ' Unknown unknown@person.com'";
  $req_select .= ")) AS destination, ";
  # Source and Destination for the Ownership
  $req_select .= "'default_node' AS source_ownership, ";
  $req_select .= "CONCAT('', IFNULL(";
  $req_select .= "CONCAT(usr_info.user_id), ' Unknown unknown@person.com'";
  $req_select .= ")) AS destination_ownership, ";Payment Mode/
  */

  $req_select .= "CONCAT('', payment_method_name) AS payment_method, ";
  $req_select .= "IF (usr_info.company is not NULL, usr_info.company, '') AS shipping_company, ";
  $req_select .= "IF (usr_info.first_name is not NULL, usr_info.first_name, '') AS shipping_firstname, ";
  $req_select .= "IF (usr_info.last_name is not NULL, usr_info.last_name, '') AS shipping_lastname, ";
  $req_select .= "IF (usr_info.country is not NULL, shipping_ctr.country_name, '') AS shipping_country, ";
  $req_select .= "IF (usr_info.user_email is not NULL, usr_info.user_email, '') AS user_email, ";

  $req_select .= "IF (ord_usr.company is not NULL, ord_usr.company, '') AS billing_company, ";
  $req_select .= "IF (ord_usr.first_name is not NULL, ord_usr.first_name, '') AS billing_firstname, ";
  $req_select .= "IF (ord_usr.last_name is not NULL, ord_usr.last_name, '') AS billing_lastname, ";
  $req_select .= "IF (ord_usr.country is not NULL, billing_ctr.country_name, '') AS billing_country, ";
  $req_select .= "IF (ord_usr.user_email is not NULL, ord_usr.user_email, '') AS billing_user_email, ";
  
  //$req_select .= "'type/Sale Order' AS category, ";
  //$req_select .= "NOW() AS start_date ";
  $req_select .= "DATE_FORMAT(ordr.cdate , '%Y/%m/%d') AS start_date " ;
  //$req_select .= "DATE_FORMAT(ordr.cdate , '%Y/%m/%d') AS start_date, ";
  $req_select .= "FROM ".constant('_VM_TABLE_PREFIX_')."_orders ordr ";
  $req_select .= "LEFT JOIN ".constant('_JOOMLA_TABLE_PREFIX_')."users usr ON ordr.user_id=usr.id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_user_info usr_info ON usr_info.user_info_id=ordr.user_info_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_vendor vdr ON ordr.vendor_id=vdr.vendor_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_order_payment pyt ON ordr.order_id=pyt.order_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_payment_method pmt ON pyt.payment_method_id=pmt.payment_method_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_order_user_info ord_usr ON ordr.order_id=ord_usr.order_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_country shipping_ctr ON usr_info.country=shipping_ctr.country_3_code ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_country billing_ctr ON ord_usr.country=billing_ctr.country_3_code ";
  $req_select .= "WHERE (order_status  = 'C' OR  order_status  = 'S' OR  order_status  = 'P')";
  if($order_id != "") 
    $req_select .= "AND ordr.order_id = '".$order_id."'";
  $req_select .= "ORDER BY ordr.order_id DESC";

  //echo $req_select;
  header('Content-type: text/xml');
  echo executeSQL($req_select);

  mysql_close();
 ?>