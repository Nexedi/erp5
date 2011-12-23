<?php
include('database.php');

$id = "";
$street = ""; 
$zip = "";
$city = "";
$country = "";

if (isset($_POST['id'])) {
    $id = $_POST['id'];
}
if (isset($_POST['street'])) {
    $street = $_POST['street'];
}
if (isset($_POST['zip'])) {
    $zip = $_POST['zip'];
}
if (isset($_POST['city'])) {
    $city = $_POST['city'];
}
if (isset($_POST['country'])) {
    $country = $_POST['country'];
}

if (($id!="") and ($country!="")){
  $req_exist_country = mysql_query("SELECT * from uc_countries where country_name=$country") or die(mysql_error());
  $country_rows = mysql_num_rows($req_exist_country);
  if ($country_rows != 0){
    $result_country = mysql_fetch_array($req_exist_country);
    $country_id =  $result_country["country_id"];
  }else{
    $country = getCountriesInfo($country);
    $country_id = 0;
    if (!empty($country)){
      $country_id = $country["numcode"];
      $country_name = $country["printable_name"];
      $country_iso_code_2 = $country["iso2"];
      $country_iso_code_3 = $country["iso3"];
      $country_sql = sprintf("INSERT INTO uc_countries (country_id, country_name, country_iso_code_2, country_iso_code_3, version) VALUES (%d, %s, %s, %s, %d)", 
	      GetSQLValueString($country_id,"int"), 
	      GetSQLValueString($country_name,"text"), 
	      GetSQLValueString($country_iso_code_2,"text"), 
	      GetSQLValueString($country_iso_code_3,"text"),
	      GetSQLValueString(1,"int")); 
      mysql_query($country_sql) or die(mysql_error());
    }   
  }
  $customer_sql = sprintf("UPDATE uc_orders set billing_street1=%s, billing_city=%s, billing_postal_code=%d,  billing_country=%d WHERE order_id=%d", 
	  GetSQLValueString($street,"text"), 
	  GetSQLValueString($city,"text"), 
	  GetSQLValueString($zip,"int"), 
	  GetSQLValueString($country_id,"text"),
	  GetSQLValueString($id,"int")); 
  mysql_query($customer_sql) or die(mysql_error());
}  
?>