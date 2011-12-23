<?php
  include('tiosafe_config.php');

  if(postNotEmpty ('person_id')) {
        $customers_id = $_POST['person_id'];

        // XXX remove all reference FROM others tables
        $db->Execute("update " . TABLE_REVIEWS . "
                        set customers_id = null
                        WHERE customers_id = '" . (int)$customers_id . "'");
        // Removing all the addresses associated with the given customer id
        $db->Execute("DELETE FROM " . TABLE_ADDRESS_BOOK . "
                      WHERE customers_id = '" . (int)$customers_id . "'");
        
        // Remove the customer FROM the customers table
        $db->Execute("DELETE FROM " . TABLE_CUSTOMERS . "
                      WHERE customers_id = '" . (int)$customers_id . "'");

        $db->Execute("DELETE FROM " . TABLE_CUSTOMERS_INFO . "
                      WHERE customers_info_id = '" . (int)$customers_id . "'");

        $db->Execute("DELETE FROM " . TABLE_CUSTOMERS_BASKET . "
                      WHERE customers_id = '" . (int)$customers_id . "'");

        $db->Execute("DELETE FROM " . TABLE_CUSTOMERS_BASKET_ATTRIBUTES . "
                      WHERE customers_id = '" . (int)$customers_id . "'");

        $db->Execute("DELETE FROM " . TABLE_WHOS_ONLINE . "
                      WHERE customer_id = '" . (int)$customers_id . "'");
  }
  else 
    echo '\nInvalid query: Parameter person_id is required!';

  $db->close();
?>
