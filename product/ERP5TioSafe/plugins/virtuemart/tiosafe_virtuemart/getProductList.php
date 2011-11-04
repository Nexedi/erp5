<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  

 //Get the query string and complete the SQL query AND category_name != ''
  $product_id = "";
  if(isset($_POST['product_id'])) 	
    $product_id = $_POST['product_id'];
  
  // Generate the query
  $req_select  = "SELECT DISTINCT(pdt.product_id) AS id, ";
  $req_select .= "product_name AS title, ";
  $req_select .= "product_s_desc AS description, ";
  $req_select .= "IF (product_sku is not NULL AND product_sku !='', product_sku,pdt.product_id )  AS reference ";
   //$req_select .= "product_sku AS reference ";
  $req_select .= "FROM ".constant('_VM_TABLE_PREFIX_')."_product pdt ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_product_price pce ON pdt.product_id=pce.product_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_product_category_xref cat_ref ON pdt.product_id=cat_ref.product_id ";
  $req_select .= "LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_category cat ON cat_ref.category_id=cat.category_id ";
  $req_select .= "WHERE product_name   != '' ";
  $req_select .= "AND product_sku    != '' ";
  //$req_select .= "AND category_name  != '' ";
  if($product_id!="")
    $req_select .= "AND pdt.product_id = '".$product_id."' ";
  $req_select .= "ORDER BY product_name ASC, product_sku ASC";
  
  header('Content-type: text/xml');
  echo executeSQL($req_select);

  mysql_close();
 ?>