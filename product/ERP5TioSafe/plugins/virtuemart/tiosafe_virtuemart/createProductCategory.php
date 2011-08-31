<?php
  include("includes/config.inc.php");
  include("includes/function.php");


  $product_id=$product_base_category=$product_variation=$product_price="";

  /*
  $product_id="2";
  $product_base_category="Size";
  $product_variation="XL";  
  $now = Date('dmY h:i:s');
  $fp = fopen("test.txt","a"); // ouverture du fichier en écriture
  fputs($fp, "\nProduct Category"); // on va a la ligne
  fputs($fp, $now."\n"); // on va a la ligne
  fputs($fp, $product_id." - ".$product_base_category." - ".$product_variation); // on écrit le nom et email dans le fichier
    
  fputs($fp, "\n\n"); // on va a la ligne
  fclose($fp);*/

  if(isset($_POST['product_id'])) $product_id = $_POST['product_id'];
  if(isset($_POST['base_category']))   $product_base_category = $_POST['base_category'];
  if(isset($_POST['variation']))   $product_variation = $_POST['variation'];
  if(isset($_POST['price']))   $product_price = $_POST['price'];

  
  //product_id and product_category are required
  if($product_id != "" AND $product_base_category !="" AND $product_variation !="") {
      $msg = createOrUpdateProductAttribute($product_id, $product_base_category, $product_variation, $product_price);
      echo $msg;  
    }
    else  
      echo "<xml></xml>";


 

  mysql_close();

 ?>