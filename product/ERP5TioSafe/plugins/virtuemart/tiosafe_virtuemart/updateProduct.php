<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  $product_id=$product_reference=$product_name=$product_s_desc="";
  
  if(isset($_POST['product_id'])) $product_id = $_POST['product_id'];
  if(isset($_POST['reference']))  $product_reference = $_POST['reference'];
  if(isset($_POST['title']))      $product_name = $_POST['title'];
  if(isset($_POST['description'])) $product_s_desc = $_POST['description'];
  
   //Product id is required
   if ($product_id !="") {
    // if ref doesn't exists create, reference is unique
      $prod_id=referenceExists($product_reference);
      //echo "Prod_id: ".$prod_id;
      if($prod_id==$product_id)
      {
         // Update the title
        if($product_name != "") {
          $productUpdateQuery1a = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_product 
                                   SET product_name=%s
                                   WHERE product_id=%s",
                                   GetSQLValueString($product_name, "text"), 
                                   GetSQLValueString($product_id, "int"));
          //echo $productUpdateQuery1a;
          $msg1a = executeSQL($productUpdateQuery1a);
        }
        if($product_s_desc != "") {
          $productUpdateQuery1b = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_product 
                                   SET product_s_desc=%s
                                   WHERE product_id=%s",
                                   GetSQLValueString($product_s_desc, "text"), 
                                   GetSQLValueString($product_id, "int"));
          //echo $productUpdateQuery1b;
          $msg1b = executeSQL($productUpdateQuery1b);
        }
      } 
      elseif($prod_id!="" && $prod_id!=$product_id) {
        echo '<xml><error>Virtuemart Error:  Reference already exists!</error></xml>';
   }
   else {
        if($product_name != "") {
         // Update the new reference
         $productUpdateQuery2a = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_product 
                                   SET product_name=%s
                                   WHERE product_id=%s",
                                   GetSQLValueString($product_name, "text"), 
                                   GetSQLValueString($product_id, "int"));
        } 
       //echo $productUpdateQuery2a;
       $msg2a= executeSQL($productUpdateQuery2a);


       if($product_s_desc != "") {
         // Update the new reference
         $productUpdateQuery2b = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_product 
                                   SET product_s_desc=%s
                                   WHERE product_id=%s",
                                   GetSQLValueString($product_s_desc, "text"), 
                                   GetSQLValueString($product_id, "int"));
        } 
       //echo $productUpdateQuery2b;
       $msg2b = executeSQL($productUpdateQuery2b);

      }
   
      echo "<xml></xml>";
     
   }
   else 
    echo '<xml><error>Invalid query: product_id is required!</error></xml>';

  mysql_close();

 ?>