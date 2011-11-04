<?php

/**
* Execute query and sql query
*
* @return xml if the query is a Select, a result message if not
*/
function executeSQL($sql, $db)
{

   $query_type = explode(" ", trim($sql));
    
   $result = $db->Execute($sql);

   if (!$result) {
        die('\nInvalid query: '.$sql.' '. mysql_error());
   }
   
   switch(strtoupper($query_type[0])) {
    case "SELECT":
      if($result->RecordCount() > 0) {
        $xml = '<xml>';
        while (!$result->EOF) {
          $xml .= '<object>';
          /*print_r($result->fields);*/
          
          foreach ($result->fields as $fieldname => $fieldvalue) {
            if(!empty($fieldvalue))
              $xml .= '<'.$fieldname.'>'. sanitizeStringForXML($fieldvalue) .'</'.$fieldname.'>';
          }
          $xml .= '</object>';
          $result->MoveNext();
        }
        $xml .= '</xml>';
     }
     else
       $xml="<xml></xml>";
       //$xml="\nNo record for your query!";
     return $xml;
    
    break;
    /*case "INSERT":
    break;
    case "DELETE":
    break; */
    default: // In the case no objects is return, return an OK message
     $xml = "\nQuery successfully processed!";
     return $xml;
    break;
  } //End switch

}


/**
* get store name
*
* @return string,  name of the store, false if not found
*/

function getStoreName ($db) {
      $query = $db->Execute("SELECT configuration_value
                              FROM " . TABLE_CONFIGURATION . "
                              WHERE configuration_key = 'STORE_NAME'");
      if ($query->RecordCount() > 0) {
        return $query->fields['configuration_value'];
      }
      else 
        return false;
}

/**
* clean up a text to avoid xml reading error
*
* @return string, cleaned text
*/

function sanitizeStringForXML ($string) {
      $special_cars = array('&', '<', '>');
      $replace_cars = array('&amp;', '&lt;', '&gt;');
      $string = str_replace($special_cars, $replace_cars, $string);
      return $string;
}


/**
* get a country's id in zencart
*
* @return interger, id of the country witch name is $country_name, false if not
*/

function getCountryId ($country_name, $db) {
      $query = $db->Execute("SELECT countries_id
                              FROM " . TABLE_COUNTRIES . "
                              WHERE countries_name = '" . $country_name . "'");
      if ($query->RecordCount() > 0) {
        return $query->fields['countries_id'];
      }
      else 
        return false;
}

/**
* get a the default language of zencart
*
* @return interger, id of the default language, false if not
*/
function getDefaultLanguageID ($db) {
   $query = $db->Execute("SELECT languages_id
                              FROM " . TABLE_LANGUAGES . "
                              WHERE code = (SELECT configuration_value FROM " . TABLE_CONFIGURATION . " WHERE configuration_key = 'DEFAULT_LANGUAGE')");
      if ($query->RecordCount() > 0) {
        return $query->fields['languages_id'];
      }
      else 
        return false;
}


/**
* Get the category erp5 like path  
*
* @return String, category_path, 
*/
function getCategoryERP5LikePath($category_id, $parent_id=0) {
  
    //if ($parent_id == '0') 
      //echo getCategoryName($category_id)."/";

    $sSql = "SELECT parent_id, categories_name  
             FROM ". TABLE_CATEGORIES ." cat
             LEFT JOIN ". TABLE_CATEGORIES_DESCRIPTION ." cat_desc
             ON cat.parent_id = cat_desc.categories_id
             WHERE cat.categories_id=$category_id
             AND parent_id != '0' ";
    $req = mysql_query($sSql) or die(mysql_error()." - Req: ".$sSql);

    if (mysql_num_rows($req)>0)
    {   
  $aData = mysql_fetch_assoc($req);
        return getCategoryERP5LikePath($aData['parent_id'], $aData['parent_id'])."/".$aData['categories_name'];
    }

}




/* Same rules as the funtion above : getDefaultLanguageID()*/
function getCurrencyValue ($currencyName) {
  $query = 'SELECT value FROM ' . TABLE_CURRENCIES . ' WHERE code = "' . $currencyName . '"';
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
	      if ( empty($set_update) ) $set_update .= $db_update_list[$key] . ' = "' . zen_db_prepare_input($_POST[$value]) . '"';
	      else $set_update .= ',' . $db_update_list[$key] . ' = "' . zen_db_prepare_input($_POST[$value]) . '"';
	  }
  }
  return $set_update;
}

/* In order to use this function ('../includes/functions/password_funcs.php') &
* ('../includes/functions/general.php')
* must be included.
* A connexion to the database must be established before.
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

function isAuthenticated() {
  if ( isset($_SERVER['PHP_AUTH_USER']) and isset($_SERVER['PHP_AUTH_PW']) ) {
	  $username = $_SERVER['PHP_AUTH_USER'];
	  $password = $_SERVER['PHP_AUTH_PW'];
	  
	  $query = 'SELECT user_password FROM ' . TABLE_ADMINISTRATORS . ' WHERE user_name = "' . $username . '"';
	  $db_query = tep_db_query($query);
	  if ( tep_db_num_rows($db_query) ) {
		  $result = tep_db_fetch_array($db_query);
		  
		  if ( tep_validate_password($password, $result['user_password']) ) {
			  return true;
		  }
	  }
  }
  return false;
}
/*
* To test if a WSR is requesting a specified file
*/
function testWSR($file, $str) {
  $myFile = fopen($file, 'w');
  fwrite($myFile, $str);
  fclose($myFile);
}
?>

