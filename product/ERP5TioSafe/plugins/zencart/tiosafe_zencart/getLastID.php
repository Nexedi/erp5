<?php
    include('tiosafe_config.php');

    if(postNotEmpty('type')) {

      $type = $_POST['type'];
      $query = "";

      switch ($type) {
        case 'Person' :
          $query = 'SELECT max(customers_id) AS last_id FROM ' . TABLE_CUSTOMERS;
          break;
        case 'Product' :
          $query = 'SELECT max(products_id) AS last_id FROM ' . TABLE_PRODUCTS;
          break;
        default :
          
      }

      header('Content-type: text/xml');
      echo executeSQL($query, $db);
    }

    $db->close();
?>
