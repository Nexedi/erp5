<?php
include('database.php');
$id = "";
$street = ""; 
$zip = 0;
$city = "";
$country_id = 0;
if (isset($_POST['id'])) {
    $id = $_POST['id'];
}
if ($id!=""){
  $customer_sql = sprintf("UPDATE uc_orders set billing_street1=%s, billing_city=%s, billing_postal_code=%d,  billing_country=%d WHERE order_id=%d", 
	  GetSQLValueString($street,"text"), 
	  GetSQLValueString($city,"text"), 
	  GetSQLValueString($zip,"int"), 
	  GetSQLValueString($country_id,"int"),
	  GetSQLValueString($id,"int")); 
  mysql_query($customer_sql) or die(mysql_error());
}  
?>