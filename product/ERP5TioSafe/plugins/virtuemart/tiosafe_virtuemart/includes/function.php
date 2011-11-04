<?php

/**
* Execute query and sql query
*
* @return xml if the query is a Select, a result message if not
*/
function executeSQL($sql)
{

   $query_type = explode(" ", trim($sql));
    
   $req = mysql_query($sql);
   if (!$req) {
        die('\nInvalid query: '.$sql.' '. mysql_error());
   }
   
   switch(strtoupper($query_type[0])) {
    case "SELECT":
      if(mysql_num_rows($req) > 0) {
        $xml = '<xml>';
        while ($row = mysql_fetch_assoc($req)) {
          $xml .= '<object>';
          foreach ($row as $fieldname => $fieldvalue) {
            $xml .= '<'.$fieldname.'>'.$fieldvalue.'</'.$fieldname.'>';
          }
          $xml .= '</object>';
        }
        $xml .= '</xml>';
     }
     else
       $xml="<xml></xml>";
     return $xml;
    
    break;
    /*case "INSERT":
    break;
    case "DELETE":
    break; */
    default: // In the case no objects is return, return an OK message
     $xml = "<xml>Done</xml>";
     return $xml;
    break;
  } //End switch

}


/**
* Test if a person has a default address in VirtueMart 1.1.4 users
*
* @return a boolean true if the user exists, false if not
*/
function isDefaultAddressSet($user_id) {
   /*exit( "SELECT address_1, zip, country, city 
                                             FROM ".constant('_VM_TABLE_PREFIX_')."_user_info 
                                             WHERE user_id='$user_id' AND address_type='BT'");*/
   if($result=mysql_query("SELECT address_1, zip, country, city 
                             FROM ".constant('_VM_TABLE_PREFIX_')."_user_info 
                             WHERE user_id='".$user_id."' AND address_type='BT'"))
    {  $row=mysql_fetch_array($result);
      if($row['address_1'] == "no_street" AND
         $row['zip'] == "no_zip" AND
         $row['country'] == "no_country" AND
         $row['city'] == "no_city")
        $ret = false;
      else 
        $ret = true;
    } else
        $ret = false;

   return $ret;
}

/**
* Test if an address is a person's default one in VirtueMart 1.1.4 users
*
* @return a boolean true if the address is the default, false if not
*/
function isAddressDefault($user_info_id) {
   if($user_info_id=="" OR !($result=mysql_query("SELECT address_type FROM ".constant('_VM_TABLE_PREFIX_')."_user_info WHERE user_info_id='$user_info_id'"))
     )
    {
      $row=mysql_fetch_array($result);
      if($row['address_type'] == "BT")
        return true;
      else 
        return false;
    }
}

/**
* Test if an email exists in VirtueMart 1.1.4 users
*
* @return int An integer user_id if the user exists, false if not
*/
function emailExists($user_email) {
  //if a product with a reference $category exists return 1
  // else return 0
  //echo "SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_user_info WHERE username ='$username'";
  if($user_email=="" 
     OR !($result=mysql_query("SELECT id FROM ".constant('_JOOMLA_TABLE_PREFIX_')."users WHERE email='$user_email'"))
    )
    {
      return false;
    }
   $row=mysql_fetch_array($result);
   return $row['id'];
}

/**
* Test if a product reference exists in VirtueMart 1.1.4 
*
* @return int An integer, the product_id if the reference exists, false if not
*/
function referenceExists($reference) {
  //if a product with a reference $category exists return 1
  // else return 0
  //echo "SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_product WHERE product_sku='$reference'";
  if($reference=="" OR !($result=mysql_query("SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_product WHERE product_sku='$reference'")))
    {
      return false;
    }
   $row=mysql_fetch_array($result);
   return $row['product_id'];
}

/**
* Test if a category exists in VirtueMart 1.1.4 
*
* @return int An integer, the category_id if the category exists, false if not
*/
function categoryExists($category) {
  //if the category $category exists in VM return the row
  // else return 0
  if(!($result=mysql_query("SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_category WHERE category_name='$category'")))
    {
      return false;
    }
    $row=mysql_fetch_array($result);
    return $row['category_id'];
}


/**
* Test if a price has been set for a product in VirtueMart 1.1.4 
*
* @return int An integer, the product_price_id if the price was set, false if not
*/
function priceExists($product_id) {
  //if a product with a reference $category exists return 1
  // else return 0
  if(!($result=mysql_query("SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_product_price WHERE product_id='$product_id'")))
    {
      return false;
    }
   $row=mysql_fetch_array($result);
   return $row['product_price_id'];
}


/**
* Test if a relationship exists between a product and a category in VirtueMart 1.1.4 
*
* @return boolean true if the price was set, false if not
*/
function categoryProductLinkExists($category_id, $product_id) {
 //if a product with a reference $category exists return 1
  // else return 0
  if(!($result=mysql_query("SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_product_category_xref 
                            WHERE category_id='$category_id' AND product_id='$product_id'")))
    {
      return false;
    }
   return true;
}


/**
* Get the last insert id of and auto incremente column VirtueMart 1.1.4 
*
* @return Integer, last insert id, false if not
*/
function getLastId($table, $champ) {
  if(!($result=mysql_query("SELECT MAX(".$champ.") as id FROM ".$table."")))
    {
      return false;
    }
   $row=mysql_fetch_array($result);
   return ($row['id']+1);
}

/**
* Get the category erp5 like path  
*
* @return String, category_path, 
*/
function getCategoryPath($category_id, $parent_id) {
  
    //if ($parent_id == '0') 
      //echo getCategoryName($category_id)."/";

    $sSql = "SELECT category_parent_id, category_name
             FROM ".constant('_VM_TABLE_PREFIX_')."_category_xref cat_xref
             LEFT JOIN ".constant('_VM_TABLE_PREFIX_')."_category cat 
             ON cat_xref.category_parent_id = cat.category_id
             WHERE category_child_id=$category_id
             AND category_parent_id != '0' ";
    $req = mysql_query($sSql) or die(mysql_error()." - Req: ".$sSql);

    if (mysql_num_rows($req)>0)
    {   
	$aData = mysql_fetch_assoc($req);
        return getCategoryPath($aData['category_parent_id'], $aData['category_parent_id'])."/".$aData['category_name'];
    }

}


/**
* Get the category name  
*
* @return String, category_name, 
*/
function getCategoryName($category_id) {
  
    $sSql = "SELECT  category_name
             FROM ".constant('_VM_TABLE_PREFIX_')."_category cat 
             WHERE category_id=$category_id";
    $req = mysql_query($sSql) or die(mysql_error()." - Req: ".$sSql);

    if (mysql_num_rows($req)>0)
    {   
        $aData = mysql_fetch_assoc($req);
        //$val= $aData['category_parent_id'];
        return $aData['category_name'];
    }
}

/**
* Get the category of a product
*
* @return Integer, category_id, false if not found
*/
function getProductCategoryIdList($product_id) {

  if(!($result=mysql_query("SELECT * FROM ".constant('_VM_TABLE_PREFIX_')."_product_category_xref 
                            WHERE product_id='$product_id'")))
    {
      return false;
    }
   //XXX In the case of a list, return the a list
   $row=mysql_fetch_array($result);
   return $row['category_id'];
}

/**
* Get the attributes of a product as erp5 category
*
* @return String, formatted category_list size/L, size/XL, color/blue, 
*/
function getProductAttributeFormattedList($product_id) {

  if(!($result=mysql_query("SELECT attribute FROM ".constant('_VM_TABLE_PREFIX_')."_product 
                            WHERE product_id='$product_id'")))
    {
      return false;
    }
   //XXX In the case of a list, return the a list
   $row=mysql_fetch_array($result);

   $erp5_category_list = "";
   //Get the attributes
   $attribute_list = explode(';', $row['attribute']);
   
   //Get attribute values
   foreach($attribute_list as $attribute ) {
     $attribute_value_list= explode(',', $attribute);
     $attribute_name = $attribute_value_list[0];
     for($i=1;$i<count($attribute_value_list);$i++) {
       //Process the prize if exists
       $attribute_value=$attribute_value_list[$i];
       $pos = stripos($attribute_value_list[$i], '[');
       if( $pos !== false) { //$pos != false  Or $pos type != false
           $attribute_value = substr($attribute_value, 0, $pos);
           //$price = substr($attribute_value_list[$i], $pos, strlen($attribute_value_list[$i])-2);
           //$erp5_category_list .= '<variation><sale_price>'.$price.'</sale_price>';
      }
                 
       $erp5_category_list .= '<object><category>'.$attribute_name.'/'.$attribute_value.'</category></object>';
       $j++;
     }
     
    }
    return $erp5_category_list;
}

/**
* Create an attribute of a product 
*
* @return int, parameter erp5_variation like size/L, size/XL, color/blue, 
*/
function createOrUpdateProductAttribute($product_id, $product_base_categ, $product_variation, $prize) {

  if(!($result=mysql_query("SELECT attribute FROM ".constant('_VM_TABLE_PREFIX_')."_product 
                            WHERE product_id='$product_id'")))
    {
      return false;
    }

   
   $row=mysql_fetch_array($result);
   $vm_category_list = "";


  //XXX Use the same base category name color or colour in
  // both erp5 and virtuemart
  if(strtolower($product_base_categ)=='colour') $product_base_categ='Color';


  if($row['attribute'] != "") {
   //Get the attributes
   $attribute_list = explode(';', $row['attribute']);
   $found = false;
   //print_r( $attribute_list);
   // test if the attribute already exists
   
   $pos = strpos($row['attribute'], ",".$product_variation);
   if( $pos === false) {//attribute doesn't exist yet
     //print_r($attribute_list);
     //Get attribute values
     foreach($attribute_list as $attribute ) { 
       $attribute_value_list= explode(',', $attribute);
       $attribute_name = $attribute_value_list[0];
       
       if (strtolower($attribute_name) === strtolower($product_base_categ)) {
          if($prize != "")   
            $vm_category_list .= $attribute.",".$product_variation."[=".$prize.".00];";
          else 
             $vm_category_list .= $attribute.",".$product_variation.";";      

          $found = true; 
       } 
       else
           $vm_category_list .= $attribute.";";
     }
 
     if(!$found) {
      $vm_category_list.= $product_base_categ.",".$product_variation.";";
     }
       
   }
   else  //attribute already exists
   {
      foreach($attribute_list as $attribute ) { 
       
       $attribute_value_list= explode(',', $attribute);
       $attribute_name = $attribute_value_list[0];
       
       $updated_attibute=$attribute_name;

       if (strtolower($attribute_name) === strtolower($product_base_categ)) {
        for ($i=1; $i<count($attribute_value_list); $i++) {
            $vm_variation = $attribute_value_list[$i];

            if(StartsWith($vm_variation, $product_variation)) {
              //$updated_attibute.=$vm_variation;
              $vm_variation_details=explode('[', $vm_variation);
              if($prize != "")   
               $updated_attibute.=",".$vm_variation_details[0]."[=".$prize.".00]";
              else 
               $updated_attibute.= ",".$vm_variation;
            } 
            else 
             $updated_attibute.=",".$vm_variation;
            
         }
        $vm_category_list .= $updated_attibute.";";
       }
       else
        $vm_category_list .= $attribute.";";
      }
   }

  }//Attribute list is empty, then create
  else
  {
   $vm_category_list .= "".$product_base_categ.",".$product_variation.";";;
  }


   if($vm_category_list != "") {
      if(substr($vm_category_list, strlen($vm_category_list)-1,1)==";")
        $vm_category_list = substr($vm_category_list, 0, strlen($vm_category_list)-1);

      $attributeUpdateQuery1a = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_product 
                                      SET attribute=%s
                                      WHERE product_id=%s",
                                      GetSQLValueString($vm_category_list, "text"), 
                                      GetSQLValueString($product_id, "int"));
      ////echo $attributeUpdateQuery1a;
      $msg1a = executeSQL($attributeUpdateQuery1a);
      return $msg1a;
   }
   else
     return "<xml><error>Query not executed</error></xml>";
   
   
}


/**
* Create an attribute of a product 
*
* @return int, parameter erp5_variation like size/L, size/XL, color/blue, 
*/
function deleteProductAttribute($product_id, $product_base_categ, $product_variation) {

  if(!($result=mysql_query("SELECT attribute FROM ".constant('_VM_TABLE_PREFIX_')."_product 
                            WHERE product_id='$product_id'")))
    {
      return false;
    }

   
   $row=mysql_fetch_array($result);
   $vm_category_list = "";
   //Get the attributes
   $attribute_list = explode(';', $row['attribute']);
     
   // test if the attribute already exists
   $pos = strpos(strtolower($row['attribute']), ",".strtolower($product_variation));
   if( $pos > 0) { //attribute already exists
   
      foreach($attribute_list as $attribute ) { 
       
       $attribute_value_list= explode(',', $attribute);
       $attribute_name = $attribute_value_list[0];
       
       $updated_attibute="";
       
       if (strtolower($attribute_name) === strtolower($product_base_categ)) {
        $updated_attibute=$attribute_name;
        for ($i=1; $i<count($attribute_value_list); $i++) {
            $vm_variation = $attribute_value_list[$i];
            if(!StartsWith($vm_variation, $product_variation)) {
              $updated_attibute.=",".$vm_variation;
              //echo $updated_attibute."<br>";
            }             
         }
        $vm_category_list .= $updated_attibute.";";
       }
       else
        $vm_category_list .= $attribute.";";
      }
   }


   if($vm_category_list != "") {
      $vm_category_list = substr($vm_category_list, 0, strlen($vm_category_list)-1);

      $attributeUpdateQuery = sprintf("UPDATE ".constant('_VM_TABLE_PREFIX_')."_product 
                                      SET attribute=%s
                                      WHERE product_id=%s",
                                      GetSQLValueString($vm_category_list, "text"), 
                                      GetSQLValueString($product_id, "int"));
      //echo $attributeUpdateQuery;
      $msg = executeSQL($attributeUpdateQuery);
      return $msg;
   }
   else
    return "<xml><error>Query not executed</error></xml>";
}



/**
* Get the country code  
*
* @return String, country_code, 
*/
function getCountryCode($country_name) {
  
    $sSql = "SELECT  country_3_code
             FROM ".constant('_VM_TABLE_PREFIX_')."_country ctr 
             WHERE country_name LIKE '".$country_name."'";
    //echo $sSql;
    $req = mysql_query($sSql) or die(mysql_error()." - Req: ".$sSql);

    if (mysql_num_rows($req)>0)
    {   
        $aData = mysql_fetch_assoc($req);
        //$val= $aData['category_parent_id'];
        return $aData['country_3_code'];
    }
    else
        return $country_name;
}


function StartsWith($Haystack, $Needle){
    // Recommended version, using strpos
    return strpos($Haystack, $Needle) === 0;
}


/**
* Prepare sql query params 
*
* @return prepared param in the good format
*/
function GetSQLValueString($theValue, $theType, $theDefinedValue = "", $theNotDefinedValue = "") 
{
  $theValue = (!get_magic_quotes_gpc()) ? addslashes($theValue) : $theValue;
  switch ($theType) {
    case "text":
      $theValue = ($theValue != "") ? "'" . $theValue . "'" : "NULL";
      break;    
    case "long":
    case "int":
      $theValue = ($theValue != "") ? intval($theValue) : "NULL";
      break;
    case "double":
      $theValue = ($theValue != "") ? "'" . doubleval($theValue) . "'" : "NULL";
      break;
    case "date":
      $theValue = ($theValue != "") ? "'" . $theValue . "'" : "NULL";
      break;
    case "defined":
      $theValue = ($theValue != "") ? $theDefinedValue : $theNotDefinedValue;
      break;
  }
  return $theValue;
}


?>
