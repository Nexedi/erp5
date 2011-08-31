<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  $product_reference=$product_name=$product_price=$product_category="";
  if(isset($_POST['reference']))  $product_reference = $_POST['reference'];
  if(isset($_POST['title']))      $product_name = $_POST['title'];
  if(isset($_POST['sale_price'])) $product_price = $_POST['sale_price'];
  if(isset($_POST['category']))   $product_category = $_POST['category'];

  /*$now = Date('dmY h:i:s');
  $fp = fopen("test.txt","a"); // ouverture du fichier en écriture
  fputs($fp, "\nCreate Product"); // on va a la ligne
  fputs($fp, $now."\n"); // on va a la ligne
  fputs($fp, $product_reference." - ".$product_name." - ".$product_category); // on écrit le nom et email dans le fichier
  fputs($fp, "\n\n"); // on va a la ligne
  fclose($fp);*/

  
  //Title and reference are required
  if ($product_reference !="" && $product_name !="") {
    // if ref doesn't exists create, reference is unique
    
     
     if(!referenceExists($product_reference))
     {
       // Create
       $productCreateQuery1 = sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_product 
                                   (".$_PROD_PARAMS_MAPPING['reference'].", ".$_PROD_PARAMS_MAPPING['title'].",
                                    product_publish, vendor_id) 
                                   Values (%s, %s, %s, %s)",
                                   GetSQLValueString($product_reference, "text"), 
                                   GetSQLValueString($product_name, "text"),
                                   GetSQLValueString('Y', "text"),
                                   GetSQLValueString('1', "text"));
       $msg_1 = executeSQL($productCreateQuery1);
       $product_id = referenceExists($product_reference);
   
       if($product_price !="") {
          $productCreateQuery2 =  sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_product_price 
                                      (".$_PROD_PARAMS_MAPPING['id'].", ".$_PROD_PARAMS_MAPPING['sale_price'].") 
                                      Values (%s, %s)",
                                      GetSQLValueString($product_id, "int"), 
                                      GetSQLValueString($product_price, "double"));
          $msg_2 = executeSQL($productCreateQuery2);
       }
   
       /*
       if($product_category   !="") {
          //XXX category parameter can be a list
          $parent_categ_id = 0;
          $product_category_list = split('/', $product_category);
          //take off the erp5 base_category name
          unset($product_category_list[array_search(constant('_CATEGORY_INTEGRATION_MAPPING_ID_'),$product_category_list)]);
          //$product_category_list = $product_category_list
          foreach($product_category_list as  $categ_key => $categ_item) {

            $categ_id=categoryExists($categ_item);
	    if(!$categ_id)
	    { $productCreateQuery3 =  sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_category (".$_PROD_PARAMS_MAPPING['category'].", category_publish, vendor_id) Values (%s, %s, %s)",
	          			  GetSQLValueString($categ_item, "text"),
                                          GetSQLValueString('Y', "text"),
                                          GetSQLValueString('1', "text"));# required to view the category in VMart
	      $msg_3 = executeSQL($productCreateQuery3);
	      $categ_id=categoryExists($categ_item);
	    } 
	    
            // Create the link with parent category if exists
            $productCreateQuery4 =  sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_category_xref (category_parent_id, category_child_id) Values (%s, %s)",
					GetSQLValueString($parent_categ_id, "int"), 
					GetSQLValueString($categ_id, "int"));
            $msg_4 = executeSQL($productCreateQuery4);
            $parent_categ_id = $categ_id;
          }
          //Create now the link between the product and the destination category
	  $productCreateQuery5 =  sprintf("INSERT INTO ".constant('_VM_TABLE_PREFIX_')."_product_category_xref (category_id, ".$_PROD_PARAMS_MAPPING['id'].") Values (%s, %s)",
				      GetSQLValueString($categ_id, "int"), 
				      GetSQLValueString($product_id, "int"));
	  $msg_5 = executeSQL($productCreateQuery5);
        */
        
        echo $msg_1;
      }
      else
         echo '\nVirtueMart Error: A product with the reference \''.$product_reference.'\' already exists!';
  }
  else 
    echo '\nInvalid query: Title and Reference are required!';

  mysql_close();

 ?>