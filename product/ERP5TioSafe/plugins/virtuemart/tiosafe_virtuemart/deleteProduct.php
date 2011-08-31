<?php
  include("includes/config.inc.php");
  include("includes/function.php");


  $product_id = "";
  if(isset($_POST['product_id'])) $product_id = $_POST['product_id'];
 
  /*$now = Date('dmY h:i:s');
  $fp = fopen("test.txt","a");  
  fputs($fp, "\Delete Product"); 
  fputs($fp, $now."\n"); // 
  fputs($fp, $product_id." - "); 
  fputs($fp, "\n\n");
  fclose($fp);*/
  
  // Generate the query
  if ($product_id != "") {

    // Delete the customer informations
    $req_delete = "DELETE FROM ".constant('_VM_TABLE_PREFIX_')."_product WHERE product_id=".$product_id."";
    executeSQL($req_delete);
    // Delete the relationship with #_vm_price
    $req_delete1 = "DELETE FROM ".constant('_VM_TABLE_PREFIX_')."_product_price WHERE product_id=".$product_id."";
    executeSQL($req_delete1);
    // Delete the relationship with #_vm_category
    $req_delete2 = "DELETE FROM ".constant('_VM_TABLE_PREFIX_')."_product_category_xref WHERE product_id=".$product_id."";
    echo executeSQL($req_delete2);
    
    $now = Date('dmY h:i:s');
    $fp = fopen("test.txt","a"); // ouverture du fichier en écriture
    fputs($fp, "\Delete Product"); // on va a la ligne
    fputs($fp, $now."\n"); // on va a la ligne
    fputs($fp, $product_id." - ".$req_delete); // on écrit le nom et email dans le fichier
    fputs($fp, "\n\n"); // on va a la ligne
    fclose($fp);
  }
  else 
    echo '\nInvalid query: No parameter given!';

  mysql_close();

 ?>