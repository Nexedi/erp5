<?php
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');
	include_once('../includes/functions/password_funcs.php');
	include_once('../includes/functions/general.php');

	/**
	 * Getting the default language_id
	 */
	function getDefaultLanguageID () {
		$query = 'select languages_id from ' . TABLE_LANGUAGES . ' where code = (select configuration_value from ' . TABLE_CONFIGURATION . ' where configuration_key = "DEFAULT_LANGUAGE")';
		$db_query = tep_db_query($query);
		$result = tep_db_fetch_array($db_query);

		return $result['languages_id'];
	}
	
	/**
	 * Returns the value of a currency
	 */
	function getCurrencyValue ($currencyName) {
		$query = 'select value from ' . TABLE_CURRENCIES . ' where code = "' . $currencyName . '"';
		$db_query = tep_db_query($query);
		$result = tep_db_fetch_array($db_query);

		return $result['value'];
	}

	/* Checks if a field is defined in $_POST and is not empty */
	function postNotEmpty ($field) {
		if ( isset($_POST[$field]) ){
			if ( empty($_POST[$field]) ) return false;
			return true;
		}
		return false;
	}
	
	/* Checks if a field is defined in $_POST */
	function postOK($field) {
		if ( isset($_POST[$field]) ) return true;
		return false;
	}

	/* Create a formatted string with the fields to update with the respective values */
	function create_update_list ($post_update_list, $db_update_list) {
		$set_update = '';
		foreach ($post_update_list as $key => $value) {
			if ( postOK($value) ) {
			    if ( empty($set_update) ) $set_update .= $db_update_list[$key] . ' = "' . tep_db_prepare_input($_POST[$value]) . '"';
			    else $set_update .= ',' . $db_update_list[$key] . ' = "' . tep_db_prepare_input($_POST[$value]) . '"';
			}
		}
		return $set_update;
	}

	/**
	 * Authentication for admin users
	 */
	function authenticate() {
		if ( !isAuthenticated() ) {
			header('WWW-Authenticate: Basic realm="My Realm"');
	  	header('HTTP/1.0 401 Unauthorized');
			echo 'Authentication Error';
			echo '<pre>'; print_r($GLOBALS); echo '</pre>';
	  	exit;
		}
	}

  /**
   * Test if an user is authentified
   */
	function isAuthenticated() {
		if ( isset($_SERVER['PHP_AUTH_USER']) and isset($_SERVER['PHP_AUTH_PW']) ) {
			$username = $_SERVER['PHP_AUTH_USER'];
			$password = $_SERVER['PHP_AUTH_PW'];
			
			$query = 'select user_password from ' . TABLE_ADMINISTRATORS . ' where user_name = "' . $username . '"';
			$db_query = tep_db_query($query);
			if ( tep_db_num_rows($db_query) == 1) {
				$result = tep_db_fetch_array($db_query);
				
				if ( tep_validate_password($password, $result['user_password']) ) {
				return true;
				}
			}
		}
		return false;
	}

  /**
   * Retrieve the country ID by a given name
   */
	function getCountryIdByName($country_name) {
		$query = 'select countries_id from ' . TABLE_COUNTRIES . ' where countries_name LIKE "%' . $country_name . '%"';
		$db_query = tep_db_query($query);

		if ($db_query) {
			$result = tep_db_fetch_array($db_query);
			return $result['countries_id'];
		}

		return 0;
	}

  /**
   * Retrieve the default address ID of a given customer ID
   */
	function getCustomersDefaultAddressId($customers_id) {
		$query = 'select customers_default_address_id as id from ' . TABLE_CUSTOMERS . ' where customers_id = ' . $customers_id;
		$db_query = tep_db_query($query);

		if ( tep_db_num_rows($db_query) ) {
			$result = tep_db_fetch_array($db_query);
			if ( !empty($result['id']) ) return $result['id'];
		}
		return false;
	}

  /**
   * Checks if the organisation_name is included in the organisations array.
   * To avoid duplication of organisations with the same name
   */
  function isKnownOrganisation($organisations, $organisation_name) {
    if (array_key_exists($organisation_name, $organisations)) return true;
    return false;
  } 

  /**
   * Checks if an organisation is located in a given country
   */
  function isKnownCountryForOrg($organisations, $organisation_name, $country_id) {
    if (in_array($country_id, $organisations[$organisation_name])) return true;
    return false;
  }

  /**
   * Verify the existence of a tuple matching certain conditions in a given table.
   * When reindexing erp5 objects, string parameters a sent via the WSR.
   * In this case, we verify first !
   */
  function verifyExistence($table, $field, $value) {
    $query = "select $field from $table where $field = '$value'";
    $query = tep_db_query($query);

    if ( tep_db_num_rows($query) ) {
      return true;
    }
    return false;
  }

  /**
   * Checks if a base category variation exists in osC database
   */
  function optionExists($option) {
    tep_db_connect() or die('Unable to connect to database');

    $query = "select products_options_id from " . TABLE_PRODUCTS_OPTIONS . " where products_options_name LIKE '%$option%' and language_id = '" . getDefaultLanguageID() . "'";
    $query = tep_db_query($query);

    if ( tep_db_num_rows($query) ) {
      $result = tep_db_fetch_array($query);
      tep_db_close();
      return $result['products_options_id'];
    }
    tep_db_close();
    return false;
  }

  /**
   * Checks if a line category variation exists in osC database
   */
  function valueExists($value) {
    tep_db_connect() or die('Unable to connect to database');

    $query = "select * from " . TABLE_PRODUCTS_OPTIONS_VALUES . " where products_options_values_name LIKE '%$value%'";
    $query = tep_db_query($query);

    if ( tep_db_num_rows($query) ) {
      $result = tep_db_fetch_array($query);
      tep_db_close();
      return $result['products_options_values_id'];
    }
    tep_db_close();
    return false;
  }

  /**
   * Creates a base category variation in osC database
   */
  function createOption($option) {
    tep_db_connect() or die('Unable to connect to database');

    $query = "select max(products_options_id) + 1 as id from " . TABLE_PRODUCTS_OPTIONS;

    $query = tep_db_query($query);
    $result = tep_db_fetch_array($query);

    $products_options_id = $result['id'];

    $language_id = getDefaultLanguageID();
    $sql_array = array('products_options_name' => $option,
                       'products_options_id' => $products_options_id,
                       'language_id' => $language_id);

    tep_db_perform(TABLE_PRODUCTS_OPTIONS, $sql_array);

    tep_db_close();

    return $products_options_id;;
  }

  /**
   * Creates a line catgeory variation in osC database
   */
  function createValue($value) {
    tep_db_connect() or die('Unable to connect to database');

    $query = "select max(products_options_values_id) + 1 as id from " . TABLE_PRODUCTS_OPTIONS_VALUES;

    $query = tep_db_query($query);
    $result = tep_db_fetch_array($query);

    $products_options_values_id = $result['id'];
    $language_id = getDefaultLanguageID();
    $sql_array = array('products_options_values_name' => $value,
                       'language_id' => $language_id,
                       'products_options_values_id' => $products_options_values_id
    );

    tep_db_perform(TABLE_PRODUCTS_OPTIONS_VALUES, $sql_array);

    tep_db_close();

    return $products_options_values_id;
  }

  /**
   * Checks if a given base category variation is linked with a line category variation in osC
   */
  function isOptionLinkedToValue($option, $value) {
    tep_db_connect() or die('Unable to connect to database');

    $query = "select * from " . TABLE_PRODUCTS_OPTIONS_VALUES_TO_PRODUCTS_OPTIONS . " where products_options_values_id = $value and products_options_id = $option" ;
    $query = tep_db_query($query);

    if ( tep_db_num_rows($query) ) {
      tep_db_close();
      return true;
    }
    tep_db_close();
    return false;
  }

  /**
   * Checks if a given product is linked with a base category variation
   */
  function isProductLinked($option, $value, $productId) {
    tep_db_connect() or die('Unable to connect to database');

    $query = "select * from " . TABLE_PRODUCTS_ATTRIBUTES . " where options_values_id = $value and options_id = $option and products_id = $productId" ;
    $query = tep_db_query($query);

    if ( tep_db_num_rows($query) ) {
      tep_db_close();
      return true;
    }
    tep_db_close();
    return false;
  }

  /**
   * Links a base category variation with a line category variation
   */
  function createLink($option, $value) {
    tep_db_connect() or die('Unable to connect to database');

    $sql_array = array('products_options_id' => $option,
                       'products_options_values_id' => $value);

    tep_db_perform(TABLE_PRODUCTS_OPTIONS_VALUES_TO_PRODUCTS_OPTIONS, $sql_array);

    tep_db_close();
  }

  /**
   * Links a product with a base category variation
   */
  function createLinkToProduct($option, $value, $productId) {
    tep_db_connect() or die('Unable to connect to database');

    $sql_array = array('options_id' => $option,
                       'options_values_id' => $value,
                       'products_id' => $productId
                       );
    tep_db_perform(TABLE_PRODUCTS_ATTRIBUTES, $sql_array);

    tep_db_close();
  }

  /**
	 * Checks if the relation of a person to an organisation is valid
	 */

	 function isValidRelation($person_id) {
		 tep_db_connect() or die('Unable to connect to database');
		 $query = "select c.customers_id from " . TABLE_CUSTOMERS . " as c, " . TABLE_ADDRESS_BOOK . " as ab " .
		          "where c.customers_id = $person_id and c.customers_default_address_id = ab.address_book_id " .
							"and not(ab.entry_country_id = 0) and not (ab.entry_company = '')";

		 $query = tep_db_query($query);

		 if (tep_db_num_rows($query)) return true;
		 return false;
	 }
?>
