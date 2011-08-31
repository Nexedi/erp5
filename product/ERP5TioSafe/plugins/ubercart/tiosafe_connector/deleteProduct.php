<?php
include('database.php');
header('Content-Type: text/plain; charset=utf-8');

$product_table_list = array('uc_products', 
                            'uc_product_adjustments', 
                            'uc_product_attributes', 
                            'uc_product_features', 
                            'uc_product_kits', 
                            'uc_product_options',
                            'uc_product_stock',
                            'uc_quote_product_locations',
                            'node',
                            'term_node');


foreach ($product_table_list as $table){
  if (isset($_POST['product_id'])) {
      $sql = "DELETE FROM $table ";
      $sql .= "WHERE nid=".$_POST['product_id']."; ";
      $req = mysql_query($sql);
      if (!$req) {
	  die('\nInvalid query: ' . mysql_error());
      }
  }
}
if (isset($_POST['product_id'])) {
    $sql = "DELETE FROM uc_quote_shipping_types ";
    $sql .= "WHERE id=".$_POST['product_id']."; ";
    $req = mysql_query($sql);
    if (!$req) {
	die('\nInvalid query: ' . mysql_error());
    }
}
mysql_close();
?>
