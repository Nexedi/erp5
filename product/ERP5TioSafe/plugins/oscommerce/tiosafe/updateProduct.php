<?php
	include_once('functions.php');
	include_once('../includes/configure.php');
	include_once('../includes/database_tables.php');
	include_once('../includes/functions/database.php');

	if ( !postNotEmpty('id') ) die('Product Id not given');

	$products_id = $_POST['id'];

  if ( postOK('category') ) {
    $category = explode('/', $_POST['category']);
    $option = $category[0];
    $value = $category[1];

    $optionId = optionExists($option);
    $valueId = valueExists($value);

    if ( !$optionId ) {
      $optionId = createOption($option);
    }

    if ( !$valueId ) {
      $valueId = createValue($value);
    }

    if ( !isOptionLinkedToValue($optionId, $valueId) ){
      createLink($optionId, $valueId);
    }

    if ( !isProductLinked($optionId, $valueId, $products_id) ) {
      createLinkToProduct($optionId, $valueId, $products_id);
    }
    die();
  }
  tep_db_connect() or die('Unable to connect to database');

	$language_id = getDefaultLanguageID();

	$update_array = array('title');
	$db_array = array('products_name');
	$set_update = create_update_list($update_array, $db_array);
	if ( !empty($set_update) ) {
		$query = "update " . TABLE_PRODUCTS_DESCRIPTION . " set $set_update where products_id = " . $products_id . " and language_id = " . $language_id;
		tep_db_query($query);
	}

	tep_db_close();
?>
