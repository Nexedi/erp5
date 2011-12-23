<?php
  include('tiosafe_config.php');

  $products_id = "";
  if(postNotEmpty ('product_id'))
    $products_id = $_POST['product_id'];

  $language_id = getDefaultLanguageID($db);
  
  $req_select  = "SELECT pdt.products_id AS id, ";
  $req_select .= "products_name AS title, ";
  //$req_select .= "products_description AS description ";   
  $req_select .= "pdt.products_id AS reference ";
  $req_select .= "FROM ". TABLE_PRODUCTS ." pdt ";
  $req_select .= "LEFT OUTER JOIN ". TABLE_PRODUCTS_DESCRIPTION ." dsc ON pdt.products_id=dsc.products_id ";
  $req_select .= "WHERE products_name != '' ";
  $req_select .= "AND language_id = ".$language_id." ";
  if(!empty($products_id))
    $req_select .= "AND pdt.products_id = '".$products_id."' ";
  //$req_select .= "ORDER BY pdt.products_id ASC LIMIT 0, 25";

  header('Content-type: text/xml');
  echo executeSQL($req_select, $db);

  $db->close();

?>
