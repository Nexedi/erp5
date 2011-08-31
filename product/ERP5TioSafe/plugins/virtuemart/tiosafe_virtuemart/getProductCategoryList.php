<?php
  include("includes/config.inc.php");
  include("includes/function.php");

 //Get the query string and complete the SQL query
  $product_id = "8";
  if(isset($_POST['product_id']))
    $product_id = $_POST['product_id'];
  elseif(isset($_POST['group_id']))
    $product_id = $_POST['group_id'];
 
 
 if($product_id != "") {
  $xml = '<xml>';
  $xml .= getProductAttributeFormattedList($product_id);
  $xml .= '</xml>';
  header('Content-type: text/xml');
  echo $xml;
 }
 else 
   echo "<xml></xml>";

 mysql_close();
 ?>