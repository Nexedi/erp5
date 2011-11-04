<?php
  include("includes/config.inc.php");
  include("includes/function.php");

  
    $type = $_POST['type'];
    //$type = 'person';
    $query = "";

    switch ($type) {
      case 'Person' :
        $query = 'SELECT max(id) AS last_id FROM ' . constant('_JOOMLA_TABLE_PREFIX_') . 'users ';
        break;
      case 'Product' :
        $query = 'SELECT max(product_id) AS last_id FROM ' . constant('_VM_TABLE_PREFIX_') . '_product ';
        break;
      /*case 'Product' :
        $query = 'SELECT max(product_id) AS last_id FROM ' . constant('_VM_TABLE_PREFIX_') . '_product ';
        break; */
      default :
        
    }

   header('Content-type: text/xml');
   echo executeSQL($query);

   mysql_close();
 ?>