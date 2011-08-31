<?php

  //********** Conf BD
  $hostname_cnCSN = "localhost";
  $database_cnCSN = "gvi_bd";
  $username_cnCSN = "mmb";
  $password_cnCSN = "mmb";
  $cnCSN = mysql_connect($hostname_cnCSN, $username_cnCSN, $password_cnCSN) or trigger_error(mysql_error(),E_USER_ERROR); 
  //$q= mysql_query("SET SESSION SQL_LOG_UPDATE = 1");
  $db = mysql_select_db($database_cnCSN, $cnCSN) or die (mysql_error());


  // Parameters definition
 
  // Jomla! table name prefix
  define ("_JOOMLA_TABLE_PREFIX_", "gvi_");
  define ("_VM_TABLE_PREFIX_", constant('_JOOMLA_TABLE_PREFIX_')."vm");

  // ERP5 Base Category Name used to map VirtueMart Product Categories
  define ("_COLLECTION_CIM_ID_", "Collection"); // Id of the CategoryIntegration Mapping of Collection
  define ("_SIZE_BASE_CATEGORY_NAME_", "size");
  define ("_COLOR_BASE_CATEGORY_NAME_", "color");


  // Set here a mapping between tiosafe properties and fieldname
  // Use only if the field is different from the WSR param
  // $product_params_mapping = array(
  // "erp5_property" => "field_name",
  //
  $_PROD_PARAMS_MAPPING = array(
    "product_id" => "product_id",
    "title" => "product_name",
    "category" => "category_name",
    "reference" => "product_sku",
    "sale_price" => "product_price"
  );


  $_PERS_PARAMS_MAPPING = array(
    "person_id" => "user_id",
    "title" => "title",
    "firstname" => "first_name",
    "lastname" => "last_name",
    "email" => "user_email",
    //"birthday" => "",
    //"category" => "",
    "address" => "address_1",
    "street" => "address_2",
    "zip" => "zip",
    "city" => "city",
    "country" => "country",
  );

  $_ORD_PARAMS_MAPPING = array(
    "order_id" => "order_id",
    "start_date" => "cdate",
    #"stop_date" => "",
    "reference" => "order_number",
    "currency" => "order_currency",
    #"category" => "",
    "source" => "vendor_name",
    #"destination" => "customer",
    #"type" => "",
    #"resource" => "",
    "title" => "order_item_name",
    "reference" => "order_item_sku",
    "quantity" => "product_quantity",
    "price" => "product_item_price",
    "category" => "category_name",
  );


?>

