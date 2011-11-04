<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  $product_id=$product_base_category=$product_variation="";

  if(isset($_POST['product_id'])) $product_id = $_POST['product_id'];
  if(isset($_POST['base_category']))   $product_base_category = $_POST['base_category'];
  if(isset($_POST['variation']))   $product_variation = $_POST['variation'];
  
  //product_id and product_category are required
  if($product_id != "" AND $product_base_category !="" AND $product_variation !="") {

      $msg = deleteProductAttribute($product_id, $product_base_category, $product_variation);
      echo $msg;
  }
  else  
   echo "<xml></xml>";
    

  mysql_close();

 ?>